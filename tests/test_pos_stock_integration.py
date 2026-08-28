from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.models import ProductBatch, ProductStock, StockMovement, db
from app.services.sales_service import SalesService


def _seed_stock(inventory_context):
    org, store, product = inventory_context
    db.session.add_all(
        [
            ProductBatch(
                organization_id=org.id,
                product_id=product.id,
                store_id=store.id,
                batch_number="LATE",
                expiry_date=date.today() + timedelta(days=90),
                quantity=Decimal("10"),
            ),
            ProductBatch(
                organization_id=org.id,
                product_id=product.id,
                store_id=store.id,
                batch_number="EARLY",
                expiry_date=date.today() + timedelta(days=10),
                quantity=Decimal("5"),
            ),
        ]
    )
    db.session.commit()
    return org, store, product


def test_pos_sale_consumes_fefo_stock(app, inventory_context):
    _, store, product = _seed_stock(inventory_context)
    sale = SalesService().create_sale(
        [{"product_id": product.id, "quantity": "7", "unit_price": "1000"}],
        store_id=store.id,
    )
    db.session.commit()
    assert sale.total_amount == Decimal("7000")
    early = ProductBatch.query.filter_by(batch_number="EARLY").one()
    late = ProductBatch.query.filter_by(batch_number="LATE").one()
    assert early.quantity == Decimal("0")
    assert late.quantity == Decimal("8")
    movements = StockMovement.query.filter_by(reference_id=sale.id).all()
    assert sum((abs(m.quantity) for m in movements), Decimal("0")) == Decimal("7")


def test_pos_sale_rejects_insufficient_stock(app, inventory_context):
    _, store, product = inventory_context
    with pytest.raises(ValueError, match="non-expired batch stock"):
        SalesService().create_sale(
            [{"product_id": product.id, "quantity": "1"}],
            store_id=store.id,
        )
    db.session.rollback()


def test_pos_sale_without_store_keeps_legacy_behavior(app, inventory_context):
    _, _, product = inventory_context
    sale = SalesService().create_sale(
        [{"product_id": product.id, "quantity": "1", "unit_price": "100"}]
    )
    assert sale.total_amount == Decimal("100")
    db.session.rollback()
