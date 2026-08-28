"""Tenant-aware repositories for sales entities."""

from app.models import Product, Sale, SalesTarget
from app.repositories.crm_repository import TenantRepository


class ProductRepository(TenantRepository):
    model = Product


class SaleRepository(TenantRepository):
    model = Sale

    def by_period(self, start_date, end_date):
        return self.query().filter(Sale.sale_date.between(start_date, end_date)).all()


class SalesTargetRepository(TenantRepository):
    model = SalesTarget

    def for_period(self, year, month, commercial_id=None):
        query = self.query().filter_by(year=year, month=month)
        if commercial_id is not None:
            query = query.filter_by(commercial_id=commercial_id)
        return query.all()
