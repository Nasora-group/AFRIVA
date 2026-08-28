"""API tests for the tenant-scoped CRM endpoints."""

from app.api.crm import crm_api
from app.models import Client, Organization, db
from app.repositories.crm_repository import ClientRepository


def _set_tenant(monkeypatch, org):
    monkeypatch.setattr("app.api.crm.get_current_organization", lambda: org, raising=False)
    monkeypatch.setattr("app.repositories.crm_repository.get_current_organization", lambda: org)


def test_client_api_create_and_list(app, monkeypatch):
    app.register_blueprint(crm_api)
    with app.app_context():
        org = Organization(name="API Org", slug="api-org")
        db.session.add(org)
        db.session.flush()
        _set_tenant(monkeypatch, org)
        client = app.test_client()
        response = client.post("/api/v1/crm/clients", json={"name": "Pharmacie A", "phone": "770000000"})
        assert response.status_code == 201
        response = client.get("/api/v1/crm/clients")
        assert response.status_code == 200
        assert response.json["data"][0]["name"] == "Pharmacie A"


def test_client_api_rejects_missing_name(app):
    app.register_blueprint(crm_api)
    with app.app_context():
        response = app.test_client().post("/api/v1/crm/clients", json={})
        assert response.status_code == 400


def test_repository_has_no_cross_tenant_client(app, monkeypatch):
    with app.app_context():
        org_a = Organization(name="A", slug="a")
        org_b = Organization(name="B", slug="b")
        db.session.add_all([org_a, org_b])
        db.session.flush()
        db.session.add(Client(name="A only", organization_id=org_a.id))
        db.session.commit()
        _set_tenant(monkeypatch, org_b)
        assert ClientRepository().list() == []
