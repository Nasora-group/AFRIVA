"""Phase 4 CRM model and tenant-isolation tests."""

import pytest

from app import create_app
from app.models import (
    Client,
    Commercial,
    Organization,
    Prospect,
    Prospection,
    Visit,
    db,
)


class TestConfig:
    TESTING = True
    SECRET_KEY = "phase4-test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


def test_crm_models_create_and_link(app):
    org = Organization(name="Org CRM", slug="org-crm")
    db.session.add(org)
    db.session.flush()

    commercial = Commercial(
        organization_id=org.id, first_name="Awa", last_name="Diop"
    )
    client = Client(organization_id=org.id, name="Client A")
    prospect = Prospect(organization_id=org.id, name="Prospect A")
    db.session.add_all([commercial, client, prospect])
    db.session.flush()

    visit = Visit(
        organization_id=org.id,
        commercial_id=commercial.id,
        client_id=client.id,
        objective="Présentation",
        result="Intéressé",
    )
    prospection = Prospection(
        organization_id=org.id,
        commercial_id=commercial.id,
        prospect_id=prospect.id,
        reason="Ouverture de compte",
        next_action="Relance",
    )
    db.session.add_all([visit, prospection])
    db.session.commit()

    assert Visit.query.count() == 1
    assert Prospection.query.count() == 1
    assert visit.client.name == "Client A"
    assert prospection.prospect.name == "Prospect A"


def test_crm_records_are_tenant_scoped_by_repository_pattern(app):
    org_a = Organization(name="Org A", slug="crm-org-a")
    org_b = Organization(name="Org B", slug="crm-org-b")
    db.session.add_all([org_a, org_b])
    db.session.flush()
    db.session.add_all(
        [
            Client(organization_id=org_a.id, name="Client A"),
            Client(organization_id=org_b.id, name="Client B"),
        ]
    )
    db.session.commit()

    a_clients = Client.query.filter_by(organization_id=org_a.id).all()
    b_clients = Client.query.filter_by(organization_id=org_b.id).all()

    assert [client.name for client in a_clients] == ["Client A"]
    assert [client.name for client in b_clients] == ["Client B"]
    assert {client.name for client in a_clients}.isdisjoint(
        client.name for client in b_clients
    )
