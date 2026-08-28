from decimal import Decimal

from app.models import CashRegister, CashSession, Store, User, db


def _setup_register(app, organization_id):
    with app.app_context():
        user = User.query.filter_by(email="pos-tester@example.test").first()
        store = Store(
            organization_id=organization_id,
            name="Main Store",
            code="MAIN",
        )
        db.session.add(store)
        db.session.flush()
        register = CashRegister(
            organization_id=organization_id,
            store_id=store.id,
            name="Front Cash",
            code="CASH-01",
        )
        db.session.add(register)
        db.session.commit()
        return register.id, user.id


def test_open_and_close_cash_session(client, app, organization, user):
    register_id, user_id = _setup_register(app, organization.id)

    response = client.post(
        "/api/v1/pos/sessions/open",
        json={
            "register_id": register_id,
            "opened_by": user_id,
            "opening_amount": "25000.00",
        },
    )
    assert response.status_code == 201
    session_id = response.get_json()["id"]

    response = client.post(
        f"/api/v1/pos/sessions/{session_id}/close",
        json={"closed_by": user_id, "closing_amount": "31500.00"},
    )
    assert response.status_code == 200
    assert response.get_json()["status"] == "closed"


def test_second_open_session_is_rejected(client, app, organization, user):
    register_id, user_id = _setup_register(app, organization.id)
    payload = {
        "register_id": register_id,
        "opened_by": user_id,
        "opening_amount": "1000.00",
    }
    assert client.post("/api/v1/pos/sessions/open", json=payload).status_code == 201
    response = client.post("/api/v1/pos/sessions/open", json=payload)
    assert response.status_code == 400


def test_invalid_opening_amount_is_rejected(client, app, organization, user):
    register_id, user_id = _setup_register(app, organization.id)
    response = client.post(
        "/api/v1/pos/sessions/open",
        json={
            "register_id": register_id,
            "opened_by": user_id,
            "opening_amount": "-1",
        },
    )
    assert response.status_code == 400


def test_session_is_persisted_closed(client, app, organization, user):
    register_id, user_id = _setup_register(app, organization.id)
    response = client.post(
        "/api/v1/pos/sessions/open",
        json={
            "register_id": register_id,
            "opened_by": user_id,
            "opening_amount": "500.00",
        },
    )
    session_id = response.get_json()["id"]
    client.post(
        f"/api/v1/pos/sessions/{session_id}/close",
        json={"closed_by": user_id, "closing_amount": "600.00"},
    )
    with app.app_context():
        session = db.session.get(CashSession, session_id)
        assert session.status == "closed"
        assert session.closing_amount == Decimal("600.00")
