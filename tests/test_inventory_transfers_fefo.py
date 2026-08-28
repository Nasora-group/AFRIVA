from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.models import (
    Organization,
    Product,
    ProductBatch,
    ProductStock,
    Store,
    StockTransfer,
    db,
)
from app.services.inventory_service import InventoryService


def setup_inventory(app, monkeypatch):
    org = Organization(name="Transfer Org", slug="transfer-org")
    db.session.add(org)
    db.session.flush()
    source = Store(organization_id=org.id, name="Source", code="SRC")
    destination = Store(organization_id=org.id, name="Destination", code="DST")
    product = Product(
        organization_id=org.id,
        name="Pharma Product",
        sku="PH-01",
        unit_price=1000,
    )
    db.session.add_all([source, destination, product])
    db.session.flush()
    db.session.add(
        ProductStock(
            organization_id=org.id,
            product_id=product.id,
            store_id=source.id,
            quantity=Decimal("20"),
        )
    )
    db.session.commit()
    monkeypatch.setattr(
        "app.services.inventory_service.get_current_organization", lambda: org
    )
    return org, source, destination, product


def test_transfer_moves_stock_atomically(app, monkeypatch):
    _, source, destination, product = setup_inventory(app, monkeypatch)
    service = InventoryService()
    transfer = service.create_transfer(
        source.id, destination.id, [{"product_id": product.id, "quantity": "7"}]
    )
    service.complete_transfer(transfer.id)
    db.session.commit()

    stocks = ProductStock.query.filter_by(product_id=product.id).all()
    quantities = {stock.store_id: Decimal(str(stock.quantity)) for stock in stocks}
    assert quantities[source.id] == Decimal("13")
    assert quantities[destination.id] == Decimal("7")
    assert db.session.get(StockTransfer, transfer.id).status == "completed"


def test_transfer_rejects_same_store(app, monkeypatch):
    _, source, _, product = setup_inventory(app, monkeypatch)
    with pytest.raises(ValueError, match="must differ"):
        InventoryService().create_transfer(
            source.id,
            source.id,
            [{"product_id": product.id, "quantity": "1"}],
        )


def test_transfer_rejects_insufficient_stock_without_partial_commit(app, monkeypatch):
    _, source, destination, product = setup_inventory(app, monkeypatch)
    service = InventoryService()
    transfer = service.create_transfer(
        source.id, destination.id, [{"product_id": product.id, "quantity": "30"}]
    )
    with pytest.raises(ValueError, match="Insufficient source stock"):
        service.complete_transfer(transfer.id)
    db.session.rollback()
    source_stock = ProductStock.query.filter_by(
        product_id=product.id, store_id=source.id
    ).first()
    assert Decimal(str(source_stock.quantity)) == Decimal("20")


def test_fefo_consumes_earliest_expiry_first(app, monkeypatch):
    _, source, _, product = setup_inventory(app, monkeypatch)
    today = date.today()
    db.session.add_all(
        [
            ProductBatch(
                organization_id=product.organization_id,
                product_id=product.id,
                store_id=source.id,
                batch_number="LATE",
                expiry_date=today + timedelta(days=90),
                quantity=Decimal("8"),
            ),
            ProductBatch(
                organization_id=product.organization_id,
                product_id=product.id,
                store_id=source.id,
                batch_number="EARLY",
                expiry_date=today + timedelta(days=10),
                quantity=Decimal("5"),
            ),
        ]
    )
    db.session.commit()
    allocations = InventoryService().consume_fefo(product.id, source.id, "7")
    db.session.commit()
    assert allocations[0]["quantity"] == Decimal("5")
    assert allocations[1]["quantity"] == Decimal("2")


def test_fefo_ignores_expired_batches(app, monkeypatch):
    _, source, _, product = setup_inventory(app, monkeypatch)
    db.session.add(
        ProductBatch(
            organization_id=product.organization_id,
            product_id=product.id,
            store_id=source.id,
            batch_number="EXPIRED",
            expiry_date=date.today() - timedelta(days=1),
            quantity=Decimal("20"),
        )
    )
    db.session.commit()
    with pytest.raises(ValueError, match="non-expired batch stock"):
        InventoryService().consume_fefo(product.id, source.id, "1")
