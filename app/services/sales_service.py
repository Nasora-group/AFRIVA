"""Business services for products, sales and targets."""

from decimal import Decimal

from app.models import Product, Sale, SaleItem, SalesTarget, db
from app.repositories.crm_repository import ClientRepository, CommercialRepository
from app.repositories.sales_repository import (
    ProductRepository,
    SaleRepository,
    SalesTargetRepository,
)


class SalesService:
    def __init__(self):
        self.products = ProductRepository()
        self.sales = SaleRepository()
        self.targets = SalesTargetRepository()
        self.clients = ClientRepository()
        self.commercials = CommercialRepository()

    def create_product(self, **data):
        return self.products.add(Product(**data))

    def create_sale(self, items, commercial_id=None, client_id=None, **data):
        if commercial_id is not None and self.commercials.get(commercial_id) is None:
            raise ValueError("Commercial not found in current organization")
        if client_id is not None and self.clients.get(client_id) is None:
            raise ValueError("Client not found in current organization")
        if not items:
            raise ValueError("At least one sale item is required")
        sale = Sale(commercial_id=commercial_id, client_id=client_id, **data)
        total = Decimal("0.00")
        for item in items:
            product = self.products.get(item["product_id"])
            if product is None:
                raise ValueError("Product not found in current organization")
            quantity = Decimal(str(item["quantity"]))
            unit_price = Decimal(str(item.get("unit_price", product.unit_price)))
            if quantity <= 0 or unit_price < 0:
                raise ValueError("Invalid quantity or unit price")
            line_total = quantity * unit_price
            sale.items.append(
                SaleItem(
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                )
            )
            total += line_total
        sale.total_amount = total
        sale.organization_id = self.sales._organization_id()
        db.session.add(sale)
        db.session.flush()
        return sale

    def set_target(self, year, month, target_amount, commercial_id=None):
        if not 1 <= month <= 12:
            raise ValueError("month must be between 1 and 12")
        if commercial_id is not None and self.commercials.get(commercial_id) is None:
            raise ValueError("Commercial not found in current organization")
        return self.targets.add(
            SalesTarget(
                year=year,
                month=month,
                target_amount=Decimal(str(target_amount)),
                commercial_id=commercial_id,
            )
        )

    def commit(self):
        db.session.commit()
