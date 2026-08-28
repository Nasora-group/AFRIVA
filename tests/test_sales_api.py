"""API tests for sales endpoints and tenant isolation."""

from datetime import date
from decimal import Decimal

from app.api.sales import sales_api
from app.models import Client, Commercial, Organization, db


def _tenant(monkeypatch, org):
    monkeypatch.setattr(
        "app.repositories.crm_repository.get_current_organization", lambda: org
    )
    monkeypatch.setattr(
        "app.repositories.sales_repository.get_current_organization", lambda: org,
        raising=False,
    )


def _setup(app, monkeypatch):
    org = Organization(name="Sales Org", slug="sales-org")
    db.session.add(org)
    db.session.flush()
    commercial = Commercial(first_name="Sales", last_name="Rep", organization_id=org.id)
    client = Client(name="Buyer", organization_id=org.id)
    db.session.add_all([commercial, client])
    db.session.commit()
    _tenant(monkeypatch, org)
    return org, commercial, client


def _register(app):
    if "sales_api" not in app.blueprints:
        app.register_blueprint(sales_api)


def test_product_create_and_list(app, monkeypatch):
    _register(app)
    with app.app_context():
        _setup(app, monkeypatch)
        client = app.test_client()
        response = client.post(
            "/api/v1/sales/products",
            json={"name": "Produit A", "sku": "A-01", "unit_price": 1500},
        )
        assert response.status_code == 201
        response = client.get("/api/v1/sales/products")
        assert response.status_code == 200
        assert response.json["data"][0]["name"] == "Produit A"


def test_product_rejects_negative_price(app, monkeypatch):
    _register(app)
    with app.app_context():
        _setup(app, monkeypatch)
        response = app.test_client().post(
            "/api/v1/sales/products", json={"name": "Bad", "unit_price": -1}
        )
        assert response.status_code == 400


def test_sale_calculates_total(app, monkeypatch):
    _register(app)
    with app.app_context():
        _, commercial, client_row = _setup(app, monkeypatch)
        product_response = app.test_client().post(
            "/api/v1/sales/products", json={"name": "Produit", "unit_price": 1250}
        )
        product_id = product_response.json["id"]
        response = app.test_client().post(
            "/api/v1/sales/sales",
            json={
                "commercial_id": commercial.id,
                "client_id": client_row.id,
                "sale_date": date.today().isoformat(),
                "items": [
                    {"product_id": product_id, "quantity": 2},
                    {"product_id": product_id, "quantity": 1, "unit_price": 500},
                ],
            },
        )
        assert response.status_code == 201
        assert Decimal(response.json["total_amount"]) == Decimal("3000.00")
        listed = app.test_client().get("/api/v1/sales/sales")
        assert listed.status_code == 200
        assert listed.json["data"][0]["total_amount"] == "3000.00"


def test_sale_rejects_empty_items(app, monkeypatch):
    _register(app)
    with app.app_context():
        _setup(app, monkeypatch)
        response = app.test_client().post("/api/v1/sales/sales", json={"items": []})
        assert response.status_code == 400


def test_sale_rejects_foreign_client(app, monkeypatch):
    _register(app)
    with app.app_context():
        org, commercial, _ = _setup(app, monkeypatch)
        other = Organization(name="Other Sales", slug="other-sales")
        db.session.add(other)
        db.session.flush()
        foreign = Client(name="Foreign Buyer", organization_id=other.id)
        db.session.add(foreign)
        db.session.commit()
        _tenant(monkeypatch, org)
        response = app.test_client().post(
            "/api/v1/sales/sales",
            json={"commercial_id": commercial.id, "client_id": foreign.id, "items": []},
        )
        assert response.status_code == 400


def test_target_create_and_filter(app, monkeypatch):
    _register(app)
    with app.app_context():
        _, commercial, _ = _setup(app, monkeypatch)
        response = app.test_client().post(
            "/api/v1/sales/targets",
            json={"year": 2026, "month": 8, "target_amount": 40000, "commercial_id": commercial.id},
        )
        assert response.status_code == 201
        response = app.test_client().get("/api/v1/sales/targets?year=2026&month=8")
        assert response.status_code == 200
        assert response.json["data"][0]["target_amount"] == "40000.00"


def test_target_rejects_invalid_month(app, monkeypatch):
    _register(app)
    with app.app_context():
        _setup(app, monkeypatch)
        response = app.test_client().post(
            "/api/v1/sales/targets", json={"year": 2026, "month": 13, "target_amount": 1}
        )
        assert response.status_code == 400
