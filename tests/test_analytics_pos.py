from datetime import datetime, timezone
from decimal import Decimal

from app.models import POSSale, db


def test_analytics_summary_includes_confirmed_pos_sales(app, inventory_context, monkeypatch):
    org, _, register, _ = inventory_context
    pos_sale = POSSale(
        organization_id=org.id,
        session_id=register.id,
        reference="POS-BI-TEST",
        status="confirmed",
        total_amount=Decimal("250.00"),
        sold_at=datetime.now(timezone.utc),
    )
    db.session.add(pos_sale)
    db.session.commit()
    monkeypatch.setattr(
        "app.api.analytics.get_current_organization", lambda: org
    )

    response = app.test_client().get("/api/v1/analytics/summary?period=all")

    assert response.status_code == 200
    data = response.get_json()
    assert data["revenue"] == "250.00"
    assert data["sales_count"] == 1
