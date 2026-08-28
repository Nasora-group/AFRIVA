from decimal import Decimal

from app.models import CashRegister, CashSession, Organization, Payment, Product, Sale, SaleItem, Store, User, db


def _tenant(monkeypatch, org):
    monkeypatch.setattr(
        "app.services.pos_service.get_current_organization", lambda: org
    )
    monkeypatch.setattr(
        "app.repositories.crm_repository.get_current_organization", lambda: org
    )


def _setup(app, monkeypatch):
    org = Organization(name="POS Sales Org", slug="pos-sales-org")
    db.session.add(org)
    db.session.flush()
    user = User(
        email="checkout@example.test",
        password_hash="test-hash",
        first_name="Checkout",
        last_name="User",
    )
    store = Store(organization_id=org.id, name="Main Store", code="MAIN")
    db.session.add_all([user, store])
    db.session.flush()
    register = CashRegister(
        organization_id=org.id,
        store_id=store.id,
        name="Front Cash",
        code="CASH-01",
    )
    product = Product(
        organization_id=org.id,
        name="Produit POS",
        sku="POS-01",
        unit_price=1500,
    )
    db.session.add_all([register, product])
    db.session.commit()
    _tenant(monkeypatch, org)
    return org, user, register, product


def _open_session(client, register, user):
    response = client.post(
        "/api/v1/pos/sessions/open",
        json={
            "register_id": register.id,
            "opened_by": user.id,
            "opening_amount": "10000.00",
        },
    )
    assert response.status_code == 201
    return response.get_json()["id"]


def test_pos_checkout_creates_sale_lines_and_payment(app, monkeypatch):
    org, user, register, product = _setup(app, monkeypatch)
    client = app.test_client()
    session_id = _open_session(client, register, user)

    response = client.post(
        "/api/v1/pos/sales",
        json={
            "session_id": session_id,
            "items": [
                {"product_id": product.id, "quantity": 2},
                {"product_id": product.id, "quantity": 1, "unit_price": "500.00"},
            ],
            "payments": [
                {"method": "cash", "amount": "3500.00"},
                {"method": "mobile_money", "amount": "1500.00", "reference": "TX-01"},
            ],
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert Decimal(data["total_amount"]) == Decimal("3500.00")
    assert len(data["items"]) == 2
    assert len(data["payments"]) == 2
    assert data["payments"][1]["reference"] == "TX-01"

    with app.app_context():
        sale = db.session.get(Sale, data["id"])
        assert sale.organization_id == org.id
        assert sale.cash_session_id == session_id
        assert len(sale.items) == 2
        assert len(sale.payments) == 2
        assert sum((p.amount for p in sale.payments), Decimal("0.00")) == Decimal("5000.00")


def test_pos_checkout_rejects_payment_mismatch_and_rolls_back(app, monkeypatch):
    _, user, register, product = _setup(app, monkeypatch)
    client = app.test_client()
    session_id = _open_session(client, register, user)

    response = client.post(
        "/api/v1/pos/sales",
        json={
            "session_id": session_id,
            "items": [{"product_id": product.id, "quantity": 1}],
            "payments": [{"method": "cash", "amount": "1000.00"}],
        },
    )

    assert response.status_code == 400
    assert "Payment total must equal sale total" in response.get_json()["error"]
    with app.app_context():
        assert Sale.query.count() == 0
        assert SaleItem.query.count() == 0
        assert Payment.query.count() == 0


def test_pos_checkout_rejects_closed_session(app, monkeypatch):
    _, user, register, product = _setup(app, monkeypatch)
    client = app.test_client()
    session_id = _open_session(client, register, user)
    assert client.post(
        f"/api/v1/pos/sessions/{session_id}/close",
        json={"closed_by": user.id, "closing_amount": "10000.00"},
    ).status_code == 200

    response = client.post(
        "/api/v1/pos/sales",
        json={
            "session_id": session_id,
            "items": [{"product_id": product.id, "quantity": 1}],
            "payments": [{"method": "cash", "amount": "1500.00"}],
        },
    )
    assert response.status_code == 400
    assert "Open cash session not found" in response.get_json()["error"]


def test_pos_checkout_rejects_invalid_payment_method(app, monkeypatch):
    _, user, register, product = _setup(app, monkeypatch)
    client = app.test_client()
    session_id = _open_session(client, register, user)

    response = client.post(
        "/api/v1/pos/sales",
        json={
            "session_id": session_id,
            "items": [{"product_id": product.id, "quantity": 1}],
            "payments": [{"method": "crypto", "amount": "1500.00"}],
        },
    )
    assert response.status_code == 400
    assert "Unsupported payment method" in response.get_json()["error"]


def test_pos_checkout_rejects_foreign_product(app, monkeypatch):
    org, user, register, _ = _setup(app, monkeypatch)
    other = Organization(name="Other POS", slug="other-pos")
    db.session.add(other)
    db.session.flush()
    foreign_product = Product(
        organization_id=other.id,
        name="Foreign",
        sku="FOREIGN-01",
        unit_price=100,
    )
    db.session.add(foreign_product)
    db.session.commit()
    _tenant(monkeypatch, org)

    session_id = _open_session(app.test_client(), register, user)
    response = app.test_client().post(
        "/api/v1/pos/sales",
        json={
            "session_id": session_id,
            "items": [{"product_id": foreign_product.id, "quantity": 1}],
            "payments": [{"method": "cash", "amount": "100.00"}],
        },
    )
    assert response.status_code == 400
    assert "Product not found in current organization" in response.get_json()["error"]


def test_pos_checkout_rejects_zero_quantity(app, monkeypatch):
    _, user, register, product = _setup(app, monkeypatch)
    client = app.test_client()
    session_id = _open_session(client, register, user)

    response = client.post(
        "/api/v1/pos/sales",
        json={
            "session_id": session_id,
            "items": [{"product_id": product.id, "quantity": 0}],
            "payments": [{"method": "cash", "amount": "0.00"}],
        },
    )
    assert response.status_code == 400
    assert "quantity must be greater than zero" in response.get_json()["error"]
