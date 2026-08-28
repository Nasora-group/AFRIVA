"""Business services for products, sales and targets."""

from decimal import Decimal

from app.models import Product, Sale, SaleItem, SalesTarget, StockMovement, db
from app.repositories.crm_repository import ClientRepository, CommercialRepository
from app.repositories.sales_repository import (
    ProductRepository,
    SaleRepository,
    SalesTargetRepository,
)
from app.services.inventory_service import InventoryService


class SalesService:
    def __init__(self):
        self.products = ProductRepository()
        self.sales = SaleRepository()
        self.targets = SalesTargetRepository()
        self.clients = ClientRepository()
        self.commercials = CommercialRepository()
        self.inventory = InventoryService()

    def create_product(self, **data):
        return self.products.add(Product(**data))

    def create_sale(self, items, commercial_id=None, client_id=None, **data):
        if commercial_id is not None and self.commercials.get(commercial_id) is None:
            raise ValueError("Commercial not found in current organization")
        if client_id is not None and self.clients.get(client_id) is None:
            raise ValueError("Client not found in current organization")
        if not items:
            raise ValueError("At least one sale item is required")

        store_id = data.get("store_id")
        organization_id = self.sales._organization_id()
        sale = Sale(
            commercial_id=commercial_id,
            client_id=client_id,
            organization_id=organization_id,
            **data,
        )
        total = Decimal("0.00")
        for item in items:
            product = self.products.get(item["product_id"])
            if product is None:
                raise ValueError("Product not found in current organization")
            quantity = Decimal(str(item["quantity"]))
            unit_price = Decimal(str(item.get("unit_price", product.unit_price)))
            if quantity <= 0 or unit_price < 0:
                raise ValueError("Invalid quantity or unit price")
            if store_id is not None:
                allocations = self.inventory.consume_fefo(product.id, store_id, quantity)
            else:
                allocations = []
            line_total = quantity * unit_price
            sale.items.append(
                SaleItem(
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                    organization_id=organization_id,
                )
            )
            total += line_total
            for allocation in allocations:
                db.session.add(
                    StockMovement(
                        organization_id=organization_id,
                        product_id=product.id,
                        store_id=store_id,
                        movement_type="sale",
                        quantity=-allocation["quantity"],
                        reference_type="sale",
                        note=f"FEFO batch {allocation['batch_id']}",
                    )
                )
        sale.total_amount = total
        db.session.add(sale)
        db.session.flush()
        for movement in db.session.new:
            if isinstance(movement, StockMovement) and movement.reference_type == "sale":
                movement.reference_id = sale.id
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
