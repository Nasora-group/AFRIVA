"""API tests for the tenant-scoped CRM endpoints."""

from datetime import date

from app.api.crm import crm_api
from app.models import Client, Commercial, Contact, Organization, Prospect, Tour, db
from app.repositories.crm_repository import ClientRepository


def _set_tenant(monkeypatch, org):
    monkeypatch.setattr("app.api.crm.get_current_organization", lambda: org, raising=False)
    monkeypatch.setattr("app.repositories.crm_repository.get_current_organization", lambda: org)


def _register(app):
    if "crm_api" not in app.blueprints:
        app.register_blueprint(crm_api)


def test_client_api_create_and_list(app, monkeypatch):
    _register(app)
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
    _register(app)
    with app.app_context():
        response = app.test_client().post("/api/v1/crm/clients", json={})
        assert response.status_code == 400


def test_contact_api_create_and_list(app, monkeypatch):
    _register(app)
    with app.app_context():
        org = Organization(name="Contacts", slug="contacts")
        db.session.add(org)
        db.session.flush()
        _set_tenant(monkeypatch, org)
        client = app.test_client()
        response = client.post("/api/v1/crm/contacts", json={"first_name": "Awa", "last_name": "Diallo"})
        assert response.status_code == 201
        assert client.get("/api/v1/crm/contacts").json["data"][0]["first_name"] == "Awa"


def test_contact_api_requires_name(app):
    _register(app)
    with app.app_context():
        response = app.test_client().post("/api/v1/crm/contacts", json={"first_name": "Awa"})
        assert response.status_code == 400


def test_tour_api_create_and_list(app, monkeypatch):
    _register(app)
    with app.app_context():
        org = Organization(name="Tours", slug="tours")
        db.session.add(org)
        db.session.flush()
        commercial = Commercial(name="Commercial A", organization_id=org.id)
        db.session.add(commercial)
        db.session.flush()
        _set_tenant(monkeypatch, org)
        client = app.test_client()
        response = client.post(
            "/api/v1/crm/tours", json={"name": "Tour Dakar", "commercial_id": commercial.id}
        )
        assert response.status_code == 201
        response = client.get("/api/v1/crm/tours")
        assert response.status_code == 200
        assert response.json["data"][0]["name"] == "Tour Dakar"


def test_tour_stop_requires_target(app, monkeypatch):
    _register(app)
    with app.app_context():
        org = Organization(name="Stops", slug="stops")
        db.session.add(org)
        db.session.flush()
        commercial = Commercial(name="Commercial B", organization_id=org.id)
        db.session.add(commercial)
        db.session.flush()
        tour = Tour(name="Tour B", commercial_id=commercial.id, organization_id=org.id, tour_date=date.today())
        db.session.add(tour)
        db.session.commit()
        _set_tenant(monkeypatch, org)
        response = app.test_client().post(f"/api/v1/crm/tours/{tour.id}/stops", json={"sequence": 1})
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
