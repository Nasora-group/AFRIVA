from datetime import datetime, timezone
from decimal import Decimal

from app.models import CashSession, POSRegister, POSSale, Store, User, db


def test_analytics_summary_includes_confirmed_pos_sales(app, tenant, monkeypatch):
    user = User(email="bi-pos@example.test", password_hash="test")
    store = Store(organization_id=tenant.id, name="BI Store", code="BI-STORE")
    db.session.add_all([user, store])
    db.session.flush()
    register = POSRegister(
        organization_id=tenant.id,
        store_id=store.id,
        name="BI Register",
        code="BI-REG",
    )
    db.session.add(register)
    db.session.flush()
    session = CashSession(
        organization_id=tenant.id,
        register_id=register.id,
        opened_by=user.id,
        opening_cash=Decimal("0.00"),
    )
    db.session.add(session)
    db.session.flush()
    pos_sale = POSSale(
        organization_id=tenant.id,
        session_id=session.id,
        reference="POS-BI-TEST",
        status="confirmed",
        total_amount=Decimal("250.00"),
        sold_at=datetime.now(timezone.utc),
    )
    db.session.add(pos_sale)
    db.session.commit()
    monkeypatch.setattr(
        "app.api.analytics.get_current_organization", lambda: tenant
    )

    response = app.test_client().get("/api/v1/analytics/summary?period=all")

    assert response.status_code == 200
    data = response.get_json()
    assert data["revenue"] == "250.00"
    assert data["sales_count"] == 1
