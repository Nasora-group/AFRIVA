from datetime import datetime, timezone
from decimal import Decimal

from app.models import Client, Commercial, Sale, db


def test_analytics_summary_month_filters_sales(app, inventory_context, monkeypatch):
    org, _, _, _ = inventory_context
    commercial = Commercial(organization_id=org.id, first_name="BI", last_name="Test")
    client = Client(organization_id=org.id, name="BI Client")
    db.session.add_all([commercial, client])
    db.session.flush()

    now = datetime.now(timezone.utc)
    current = Sale(
        organization_id=org.id,
        commercial_id=commercial.id,
        client_id=client.id,
        sold_at=now,
        status="completed",
        total_amount=Decimal("100"),
    )
    old = Sale(
        organization_id=org.id,
        commercial_id=commercial.id,
        client_id=client.id,
        sold_at=now.replace(month=1),
        status="completed",
        total_amount=Decimal("900"),
    )
    db.session.add_all([current, old])
    db.session.commit()
    monkeypatch.setattr("app.api.analytics.get_current_organization", lambda: org)

    response = app.test_client().get("/api/v1/analytics/summary?period=month")

    assert response.status_code == 200
    assert response.get_json()["revenue"] == "100.00"
