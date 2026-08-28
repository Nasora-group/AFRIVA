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


def _tenant_data(app, monkeypatch):
    org = Organization(name="API Org", slug="api-org")
    db.session.add(org)
    db.session.flush()
    commercial = Commercial(first_name="A", last_name="Commercial", organization_id=org.id)
    client = Client(name="Client A", organization_id=org.id)
    prospect = Prospect(name="Prospect A", organization_id=org.id)
    db.session.add_all([commercial, client, prospect])
    db.session.commit()
    _set_tenant(monkeypatch, org)
    return org, commercial, client, prospect


def test_client_api_create_and_list(app, monkeypatch):
    _register(app)
    with app.app_context():
        _tenant_data(app, monkeypatch)
        client = app.test_client()
        response = client.post("/api/v1/crm/clients", json={"name": "Pharmacie A", "phone": "770000000"})
        assert response.status_code == 201
        response = client.get("/api/v1/crm/clients?limit=1&offset=0")
        assert response.status_code == 200
        assert len(response.json["data"]) == 1


def test_client_api_pagination_bounds(app, monkeypatch):
    _register(app)
    with app.app_context():
        _tenant_data(app, monkeypatch)
        response = app.test_client().get("/api/v1/crm/clients?limit=999&offset=-5")
        assert response.status_code == 200


def test_client_api_rejects_missing_name(app):
    _register(app)
    with app.app_context():
        response = app.test_client().post("/api/v1/crm/clients", json={})
        assert response.status_code == 400


def test_prospect_api_list(app, monkeypatch):
    _register(app)
    with app.app_context():
        _tenant_data(app, monkeypatch)
        response = app.test_client().get("/api/v1/crm/prospects")
        assert response.status_code == 200
        assert response.json["data"][0]["name"] == "Prospect A"


def test_contact_api_create_and_list(app, monkeypatch):
    _register(app)
    with app.app_context():
        _, _, client_row, _ = _tenant_data(app, monkeypatch)
        client = app.test_client()
        response = client.post(
            "/api/v1/crm/contacts",
            json={"first_name": "Awa", "last_name": "Diallo", "client_id": client_row.id},
        )
        assert response.status_code == 201
        assert client.get("/api/v1/crm/contacts").json["data"][0]["first_name"] == "Awa"


def test_contact_api_requires_name(app):
    _register(app)
    with app.app_context():
        response = app.test_client().post("/api/v1/crm/contacts", json={"first_name": "Awa"})
        assert response.status_code == 400


def test_contact_api_rejects_foreign_client(app, monkeypatch):
    _register(app)
    with app.app_context():
        org_a, _, _, _ = _tenant_data(app, monkeypatch)
        org_b = Organization(name="Other", slug="other")
        db.session.add(org_b)
        db.session.flush()
        foreign = Client(name="Foreign", organization_id=org_b.id)
        db.session.add(foreign)
        db.session.commit()
        _set_tenant(monkeypatch, org_a)
        response = app.test_client().post(
            "/api/v1/crm/contacts", json={"first_name": "X", "last_name": "Y", "client_id": foreign.id}
        )
        assert response.status_code == 404


def test_tour_api_create_and_list(app, monkeypatch):
    _register(app)
    with app.app_context():
        _, commercial, _, _ = _tenant_data(app, monkeypatch)
        client = app.test_client()
        response = client.post("/api/v1/crm/tours", json={"name": "Tour Dakar", "commercial_id": commercial.id})
        assert response.status_code == 201
        response = client.get("/api/v1/crm/tours")
        assert response.status_code == 200
        assert response.json["data"][0]["name"] == "Tour Dakar"


def test_tour_api_rejects_foreign_commercial(app, monkeypatch):
    _register(app)
    with app.app_context():
        org_a, _, _, _ = _tenant_data(app, monkeypatch)
        org_b = Organization(name="Other", slug="other")
        db.session.add(org_b)
        db.session.flush()
        foreign = Commercial(first_name="F", last_name="C", organization_id=org_b.id)
        db.session.add(foreign)
        db.session.commit()
        _set_tenant(monkeypatch, org_a)
        response = app.test_client().post("/api/v1/crm/tours", json={"name": "X", "commercial_id": foreign.id})
        assert response.status_code == 404


def test_tour_stop_requires_target(app, monkeypatch):
    _register(app)
    with app.app_context():
        _, commercial, _, _ = _tenant_data(app, monkeypatch)
        tour = Tour(name="Tour B", commercial_id=commercial.id, organization_id=commercial.organization_id, tour_date=date.today())
        db.session.add(tour)
        db.session.commit()
        response = app.test_client().post(f"/api/v1/crm/tours/{tour.id}/stops", json={"sequence": 1})
        assert response.status_code == 400


def test_tour_stop_create_for_client(app, monkeypatch):
    _register(app)
    with app.app_context():
        _, commercial, client_row, _ = _tenant_data(app, monkeypatch)
        tour = Tour(name="Tour C", commercial_id=commercial.id, organization_id=commercial.organization_id, tour_date=date.today())
        db.session.add(tour)
        db.session.commit()
        response = app.test_client().post(
            f"/api/v1/crm/tours/{tour.id}/stops", json={"sequence": 1, "client_id": client_row.id}
        )
        assert response.status_code == 201


def test_visit_requires_commercial(app):
    _register(app)
    with app.app_context():
        response = app.test_client().post("/api/v1/crm/visits", json={})
        assert response.status_code == 400


def test_visit_create_and_foreign_validation(app, monkeypatch):
    _register(app)
    with app.app_context():
        _, commercial, client_row, prospect = _tenant_data(app, monkeypatch)
        response = app.test_client().post(
            "/api/v1/crm/visits", json={"commercial_id": commercial.id, "client_id": client_row.id, "notes": "OK"}
        )
        assert response.status_code == 201
        org_b = Organization(name="Foreign", slug="foreign")
        db.session.add(org_b)
        db.session.flush()
        foreign = Client(name="Foreign", organization_id=org_b.id)
        db.session.add(foreign)
        db.session.commit()
        response = app.test_client().post(
            "/api/v1/crm/visits", json={"commercial_id": commercial.id, "client_id": foreign.id}
        )
        assert response.status_code == 404
        assert prospect.id > 0


def test_prospection_create_and_validation(app, monkeypatch):
    _register(app)
    with app.app_context():
        _, commercial, _, prospect = _tenant_data(app, monkeypatch)
        response = app.test_client().post(
            "/api/v1/crm/prospections", json={"commercial_id": commercial.id, "prospect_id": prospect.id}
        )
        assert response.status_code == 201
        response = app.test_client().post("/api/v1/crm/prospections", json={})
        assert response.status_code == 400
