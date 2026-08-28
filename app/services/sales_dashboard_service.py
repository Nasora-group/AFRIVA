"""Tenant-scoped sales dashboard metrics."""

from collections import defaultdict
from decimal import Decimal

from app.models import SalesTarget
from app.repositories.sales_repository import SaleRepository, SalesTargetRepository


class SalesDashboardService:
    def __init__(self):
        self.sales = SaleRepository()
        self.targets = SalesTargetRepository()

    def summary(self, start_date, end_date, commercial_id=None):
        rows = self.sales.by_period(start_date, end_date)
        if commercial_id is not None:
            rows = [row for row in rows if row.commercial_id == commercial_id]

        revenue = sum((row.total_amount for row in rows), Decimal("0.00"))
        by_day = defaultdict(lambda: Decimal("0.00"))
        by_commercial = defaultdict(lambda: Decimal("0.00"))
        for row in rows:
            by_day[row.sale_date.isoformat()] += row.total_amount
            if row.commercial_id is not None:
                by_commercial[row.commercial_id] += row.total_amount

        target = Decimal("0.00")
        current = start_date.replace(day=1)
        last_month = end_date.replace(day=1)
        while current <= last_month:
            for row in self.targets.for_period(current.year, current.month):
                if commercial_id is None or row.commercial_id in (None, commercial_id):
                    target += row.target_amount
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        attainment = (revenue / target * Decimal("100")) if target else Decimal("0.00")
        return {
            "revenue": revenue,
            "target": target,
            "attainment_rate": attainment,
            "sales_count": len(rows),
            "daily_revenue": dict(sorted(by_day.items())),
            "revenue_by_commercial": dict(sorted(by_commercial.items())),
        }
