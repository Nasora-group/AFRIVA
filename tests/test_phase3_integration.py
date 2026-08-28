"""Real PostgreSQL Phase 3 tenant-isolation test.

The schema and fixtures are created with the database owner, then the actual
RLS assertion is executed through a separate non-owner application role.
Only TEST_DATABASE_URL is used; production is never touched.
"""

import os
from urllib.parse import urlparse

import psycopg2
import pytest
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import Organization, OrganizationUser, Permission, Role, User, db
from app.models.role import role_permission

pytestmark = pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="TEST_DATABASE_URL is required for PostgreSQL integration tests",
)

RLS_SQL = """
ALTER TABLE role ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_user ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS role_tenant_isolation ON role;
CREATE POLICY role_tenant_isolation ON role
USING (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER)
WITH CHECK (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER);
DROP POLICY IF EXISTS organization_user_tenant_isolation ON organization_user;
CREATE POLICY organization_user_tenant_isolation ON organization_user
USING (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER)
WITH CHECK (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER);
DROP POLICY IF EXISTS activity_log_tenant_isolation ON activity_log;
CREATE POLICY activity_log_tenant_isolation ON activity_log
USING (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER)
WITH CHECK (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::INTEGER);
ALTER TABLE role FORCE ROW LEVEL SECURITY;
ALTER TABLE organization_user FORCE ROW LEVEL SECURITY;
ALTER TABLE activity_log FORCE ROW LEVEL SECURITY;
"""


def owner_connection_url():
    return os.environ["TEST_DATABASE_URL"]


def app_connection_url():
    parsed = urlparse(owner_connection_url())
    return (
        f"dbname={parsed.path.lstrip('/')} host={parsed.hostname} "
        f"port={parsed.port or 5432} user=afriva_app password=afriva_app_test"
    )


@pytest.fixture
def integration_app():
    class TestConfig:
        TESTING = True
        SECRET_KEY = "integration-only-secret"
        SQLALCHEMY_DATABASE_URI = owner_connection_url()
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SESSION_COOKIE_SECURE = False

    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def prepare_rls_and_grants():
    """Configure RLS as owner and grant only application-level table access."""
    for statement in [s.strip() for s in RLS_SQL.split(";") if s.strip()]:
        db.session.execute(text(statement))
    for table in ("organization_user", "role", "activity_log"):
        db.session.execute(text(f"GRANT SELECT ON TABLE {table} TO afriva_app"))
    db.session.commit()


def test_real_database_tenant_isolation(integration_app):
    org_a = Organization(name="Org A", slug="org-a")
    org_b = Organization(name="Org B", slug="org-b")
    db.session.add_all([org_a, org_b])
    db.session.flush()

    permission = Permission(name="clients.view")
    role_a = Role(name="Admin A", organization_id=org_a.id)
    role_b = Role(name="Admin B", organization_id=org_b.id)
    user_a = User(
        email="a@example.test", password_hash=generate_password_hash("secret")
    )
    user_b = User(
        email="b@example.test", password_hash=generate_password_hash("secret")
    )
    db.session.add_all([permission, role_a, role_b, user_a, user_b])
    db.session.flush()
    db.session.execute(
        role_permission.insert().values(role_id=role_a.id, permission_id=permission.id)
    )
    db.session.execute(
        role_permission.insert().values(role_id=role_b.id, permission_id=permission.id)
    )
    db.session.add_all(
        [
            OrganizationUser(
                user_id=user_a.id,
                organization_id=org_a.id,
                role_id=role_a.id,
            ),
            OrganizationUser(
                user_id=user_b.id,
                organization_id=org_b.id,
                role_id=role_b.id,
            ),
        ]
    )
    db.session.commit()

    prepare_rls_and_grants()

    # This connection is deliberately NOT the database owner.
    with psycopg2.connect(app_connection_url()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT set_config('app.current_organization_id', %s, false)",
                (str(org_a.id),),
            )
            cursor.execute(
                "SELECT count(*) FROM organization_user WHERE organization_id = %s",
                (org_a.id,),
            )
            assert cursor.fetchone()[0] == 1
            cursor.execute(
                "SELECT count(*) FROM organization_user WHERE organization_id = %s",
                (org_b.id,),
            )
            assert cursor.fetchone()[0] == 0
