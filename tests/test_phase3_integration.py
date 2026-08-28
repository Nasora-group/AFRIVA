"""Real PostgreSQL Phase 3 tenant-isolation test.

Only TEST_DATABASE_URL is used. Never point it at production.
"""
import os

import pytest
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db, Organization, User, OrganizationUser, Role, Permission
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
"""


@pytest.fixture
def integration_app():
    class TestConfig:
        TESTING = True
        SECRET_KEY = "integration-only-secret"
        SQLALCHEMY_DATABASE_URI = os.environ["TEST_DATABASE_URL"]
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SESSION_COOKIE_SECURE = False

    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        for statement in [s.strip() for s in RLS_SQL.split(";") if s.strip()]:
            db.session.execute(text(statement))
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


def test_real_database_tenant_isolation(integration_app):
    org_a = Organization(name="Org A", slug="org-a")
    org_b = Organization(name="Org B", slug="org-b")
    db.session.add_all([org_a, org_b])
    db.session.flush()

    permission = Permission(name="clients.view")
    role_a = Role(name="Admin A", organization_id=org_a.id)
    role_b = Role(name="Admin B", organization_id=org_b.id)
    user_a = User(email="a@example.test", password_hash=generate_password_hash("secret"))
    user_b = User(email="b@example.test", password_hash=generate_password_hash("secret"))
    db.session.add_all([permission, role_a, role_b, user_a, user_b])
    db.session.flush()
    db.session.execute(role_permission.insert().values(role_id=role_a.id, permission_id=permission.id))
    db.session.execute(role_permission.insert().values(role_id=role_b.id, permission_id=permission.id))
    db.session.add_all([
        OrganizationUser(user_id=user_a.id, organization_id=org_a.id, role_id=role_a.id),
        OrganizationUser(user_id=user_b.id, organization_id=org_b.id, role_id=role_b.id),
    ])
    db.session.commit()

    db.session.execute(text("SET LOCAL app.current_organization_id = :org"), {"org": org_a.id})
    assert db.session.execute(
        text("SELECT count(*) FROM organization_user WHERE organization_id = :org"),
        {"org": org_a.id},
    ).scalar_one() == 1
    assert db.session.execute(
        text("SELECT count(*) FROM organization_user WHERE organization_id = :org"),
        {"org": org_b.id},
    ).scalar_one() == 0
