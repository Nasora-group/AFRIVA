"""Tenant-safe inventory operations."""

from decimal import Decimal, InvalidOperation

from app.middleware.tenant_middleware import get_current_organization
from app.models import Product, ProductStock, StockMovement, Store, db


MOVEMENT_SIGN = {
    "purchase": 1,
    "return": 1,
    "adjustment": 1,
    "transfer_in": 1,
    "sale": -1,
    "transfer_out": -1,
}


class InventoryService:
    def _organization_id(self):
        organization = get_current_organization()
        if organization is None:
            raise ValueError("No current organization")
        return organization.id

    def adjust_stock(self, product_id, store_id, quantity, movement_type="adjustment", reference_type=None, reference_id=None, note=None):
        organization_id = self._organization_id()
        if movement_type not in MOVEMENT_SIGN:
            raise ValueError("Unsupported movement type")
        try:
            quantity = Decimal(str(quantity))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("quantity must be valid") from exc
        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")

        product = Product.query.filter_by(id=product_id, organization_id=organization_id, active=True).first()
        store = Store.query.filter_by(id=store_id, organization_id=organization_id, active=True).first()
        if product is None or store is None:
            raise ValueError("Product or store not found in current organization")

        stock = ProductStock.query.filter_by(
            product_id=product_id, store_id=store_id, organization_id=organization_id
        ).with_for_update().first()
        if stock is None:
            stock = ProductStock(
                organization_id=organization_id,
                product_id=product_id,
                store_id=store_id,
                quantity=Decimal("0"),
            )
            db.session.add(stock)
            db.session.flush()

        delta = quantity * MOVEMENT_SIGN[movement_type]
        new_quantity = Decimal(str(stock.quantity)) + delta
        if new_quantity < 0:
            raise ValueError("Insufficient stock")
        stock.quantity = new_quantity
        movement = StockMovement(
            organization_id=organization_id,
            product_id=product_id,
            store_id=store_id,
            movement_type=movement_type,
            quantity=delta,
            reference_type=reference_type,
            reference_id=reference_id,
            note=note,
        )
        db.session.add(movement)
        db.session.flush()
        return stock, movement
