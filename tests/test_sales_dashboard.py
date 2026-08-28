from datetime import date
from decimal import Decimal

from app.models import Sale, SalesTarget, db
from app.services.sales_dashboard_service import SalesDashboardService


def test_dashboard_service_aggregates_revenue_and_target(
    app, organization, tenant_context
):
    with app.app_context():
        sale = Sale(
            organization_id=organization.id,
            sale_date=date(2026, 8, 10),
            total_amount=Decimal("150.00"),
            status="confirmed",
        )
        target = SalesTarget(
            organization_id=organization.id,
            year=2026,
            month=8,
            target_amount=Decimal("300.00"),
        )
        db.session.add_all([sale, target])
        db.session.commit()

        metrics = SalesDashboardService().summary(
            date(2026, 8, 1), date(2026, 8, 31)
        )
        assert metrics["revenue"] == Decimal("150.00")
        assert metrics["target"] == Decimal("300.00")
        assert metrics["attainment_rate"] == Decimal("50.00")
        assert metrics["sales_count"] == 1
        assert metrics["daily_revenue"]["2026-08-10"] == Decimal("150.00")


def test_dashboard_rejects_reversed_dates(client):
    response = client.get(
        "/api/v1/sales/dashboard?start=2026-08-31&end=2026-08-01"
    )
    assert response.status_code == 400


def test_dashboard_rejects_invalid_dates(client):
    response = client.get(
        "/api/v1/sales/dashboard?start=08-01-2026&end=2026-08-31"
    )
    assert response.status_code == 400
