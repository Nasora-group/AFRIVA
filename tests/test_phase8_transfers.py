from decimal import Decimal
from datetime import date, timedelta

from app.models import ProductBatch, ProductStock, StockMovement, db
from app.services.inventory_service import InventoryService


def test_transfer_moves_stock_between_stores(app, monkeypatch, inventory_context):
    org, source, destination, product = inventory_context
    monkeypatch.setattr(
        "app.services.inventory_service.get_current_organization", lambda: org
    )
    db.session.add(
        ProductStock(
            organization_id=org.id,
            product_id=product.id,
            store_id=source.id,
            quantity=Decimal("10"),
        )
    )
    db.session.commit()

    service = InventoryService()
    transfer = service.create_transfer(
        source.id, destination.id, [{"product_id": product.id, "quantity": "4"}]
    )
    service.complete_transfer(transfer.id)
    db.session.commit()

    assert transfer.status == "completed"
    assert ProductStock.query.filter_by(store_id=source.id).one().quantity == Decimal("6")
    assert ProductStock.query.filter_by(store_id=destination.id).one().quantity == Decimal("4")
    assert StockMovement.query.filter_by(reference_id=transfer.id).count() == 2


def test_fefo_consumes_earliest_expiring_batch(app, monkeypatch, inventory_context):
    org, source, _, product = inventory_context
    monkeypatch.setattr(
        "app.services.inventory_service.get_current_organization", lambda: org
    )
    db.session.add_all(
        [
            ProductBatch(
                organization_id=org.id,
                product_id=product.id,
                store_id=source.id,
                batch_number="LATE",
                expiry_date=date.today() + timedelta(days=60),
                quantity=Decimal("5"),
            ),
            ProductBatch(
                organization_id=org.id,
                product_id=product.id,
                store_id=source.id,
                batch_number="EARLY",
                expiry_date=date.today() + timedelta(days=10),
                quantity=Decimal("3"),
            ),
        ]
    )
    db.session.commit()

    allocations = InventoryService().consume_fefo(product.id, source.id, "4")
    db.session.commit()

    assert allocations[0]["quantity"] == Decimal("3")
    assert allocations[1]["quantity"] == Decimal("1")
    assert ProductBatch.query.filter_by(batch_number="EARLY").one().quantity == Decimal("0")
    assert ProductBatch.query.filter_by(batch_number="LATE").one().quantity == Decimal("4")
