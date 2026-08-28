"""Tenant-safe inventory operations."""

from decimal import Decimal, InvalidOperation

from app.middleware.tenant_middleware import get_current_organization
from app.models import (
    Product,
    ProductBatch,
    ProductStock,
    StockMovement,
    StockTransfer,
    StockTransferItem,
    Store,
    db,
)


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

    def _quantity(self, value):
        try:
            quantity = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("quantity must be valid") from exc
        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")
        return quantity

    def adjust_stock(
        self,
        product_id,
        store_id,
        quantity,
        movement_type="adjustment",
        reference_type=None,
        reference_id=None,
        note=None,
    ):
        organization_id = self._organization_id()
        if movement_type not in MOVEMENT_SIGN:
            raise ValueError("Unsupported movement type")
        quantity = self._quantity(quantity)
        product = Product.query.filter_by(
            id=product_id, organization_id=organization_id, active=True
        ).first()
        store = Store.query.filter_by(
            id=store_id, organization_id=organization_id, active=True
        ).first()
        if product is None or store is None:
            raise ValueError("Product or store not found in current organization")
        stock = (
            ProductStock.query.filter_by(
                product_id=product_id,
                store_id=store_id,
                organization_id=organization_id,
            )
            .with_for_update()
            .first()
        )
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

    def create_transfer(
        self, source_store_id, destination_store_id, items, reference=None, note=None
    ):
        organization_id = self._organization_id()
        if source_store_id == destination_store_id:
            raise ValueError("Source and destination stores must differ")
        if not items:
            raise ValueError("At least one transfer item is required")
        stores = Store.query.filter(
            Store.id.in_([source_store_id, destination_store_id]),
            Store.organization_id == organization_id,
            Store.active.is_(True),
        ).all()
        if len(stores) != 2:
            raise ValueError("Source or destination store not found in current organization")
        transfer = StockTransfer(
            organization_id=organization_id,
            source_store_id=source_store_id,
            destination_store_id=destination_store_id,
            status="draft",
            reference=reference,
            note=note,
        )
        db.session.add(transfer)
        db.session.flush()
        for data in items:
            product_id = int(data["product_id"])
            quantity = self._quantity(data["quantity"])
            batch_id = data.get("batch_id")
            product = Product.query.filter_by(
                id=product_id, organization_id=organization_id, active=True
            ).first()
            if product is None:
                raise ValueError("Product not found in current organization")
            if batch_id is not None:
                batch = ProductBatch.query.filter_by(
                    id=int(batch_id),
                    product_id=product_id,
                    store_id=source_store_id,
                    organization_id=organization_id,
                ).with_for_update().first()
                if batch is None:
                    raise ValueError("Batch not found in source store")
                if batch.expiry_date is not None:
                    from datetime import date

                    if batch.expiry_date < date.today():
                        raise ValueError("Expired batch cannot be transferred")
                if Decimal(str(batch.quantity)) < quantity:
                    raise ValueError("Insufficient batch stock")
            transfer.items.append(
                StockTransferItem(
                    organization_id=organization_id,
                    product_id=product_id,
                    quantity=quantity,
                    batch_id=batch_id,
                )
            )
        return transfer

    def complete_transfer(self, transfer_id):
        organization_id = self._organization_id()
        transfer = StockTransfer.query.filter_by(
            id=transfer_id, organization_id=organization_id, status="draft"
        ).first()
        if transfer is None:
            raise ValueError("Draft transfer not found in current organization")
        for item in transfer.items:
            source_stock = (
                ProductStock.query.filter_by(
                    product_id=item.product_id,
                    store_id=transfer.source_store_id,
                    organization_id=organization_id,
                )
                .with_for_update()
                .first()
            )
            if source_stock is None or Decimal(str(source_stock.quantity)) < item.quantity:
                raise ValueError("Insufficient source stock")
            source_stock.quantity -= item.quantity
            destination_stock = (
                ProductStock.query.filter_by(
                    product_id=item.product_id,
                    store_id=transfer.destination_store_id,
                    organization_id=organization_id,
                )
                .with_for_update()
                .first()
            )
            if destination_stock is None:
                destination_stock = ProductStock(
                    organization_id=organization_id,
                    product_id=item.product_id,
                    store_id=transfer.destination_store_id,
                    quantity=Decimal("0"),
                )
                db.session.add(destination_stock)
                db.session.flush()
            destination_stock.quantity += item.quantity
            if item.batch_id is not None:
                source_batch = ProductBatch.query.filter_by(
                    id=item.batch_id,
                    product_id=item.product_id,
                    store_id=transfer.source_store_id,
                    organization_id=organization_id,
                ).with_for_update().first()
                if source_batch is None or source_batch.quantity < item.quantity:
                    raise ValueError("Insufficient batch stock")
                source_batch.quantity -= item.quantity
                destination_batch = ProductBatch.query.filter_by(
                    product_id=item.product_id,
                    store_id=transfer.destination_store_id,
                    batch_number=source_batch.batch_number,
                    organization_id=organization_id,
                ).with_for_update().first()
                if destination_batch is None:
                    destination_batch = ProductBatch(
                        organization_id=organization_id,
                        product_id=item.product_id,
                        store_id=transfer.destination_store_id,
                        batch_number=source_batch.batch_number,
                        expiry_date=source_batch.expiry_date,
                        quantity=Decimal("0"),
                    )
                    db.session.add(destination_batch)
                    db.session.flush()
                destination_batch.quantity += item.quantity
            db.session.add_all(
                [
                    StockMovement(
                        organization_id=organization_id,
                        product_id=item.product_id,
                        store_id=transfer.source_store_id,
                        movement_type="transfer_out",
                        quantity=-item.quantity,
                        reference_type="stock_transfer",
                        reference_id=transfer.id,
                    ),
                    StockMovement(
                        organization_id=organization_id,
                        product_id=item.product_id,
                        store_id=transfer.destination_store_id,
                        movement_type="transfer_in",
                        quantity=item.quantity,
                        reference_type="stock_transfer",
                        reference_id=transfer.id,
                    ),
                ]
            )
        transfer.status = "completed"
        db.session.flush()
        return transfer

    def consume_fefo(self, product_id, store_id, quantity):
        organization_id = self._organization_id()
        quantity = self._quantity(quantity)
        Product.query.filter_by(
            id=product_id, organization_id=organization_id, active=True
        ).first_or_404()
        from datetime import date

        batches = (
            ProductBatch.query.filter(
                ProductBatch.product_id == product_id,
                ProductBatch.store_id == store_id,
                ProductBatch.organization_id == organization_id,
                ProductBatch.quantity > 0,
                db.or_(
                    ProductBatch.expiry_date.is_(None),
                    ProductBatch.expiry_date >= date.today(),
                ),
            )
            .order_by(ProductBatch.expiry_date.asc().nullslast(), ProductBatch.id.asc())
            .with_for_update()
            .all()
        )
        remaining = quantity
        allocations = []
        for batch in batches:
            if remaining <= 0:
                break
            taken = min(Decimal(str(batch.quantity)), remaining)
            batch.quantity -= taken
            remaining -= taken
            allocations.append({"batch_id": batch.id, "quantity": taken})
        if remaining > 0:
            raise ValueError("Insufficient non-expired batch stock")
        return allocations
