from decimal import Decimal

import pytest

from app.models import Payment, ProductStock, StockMovement, db
from app.services.payment_service import PaymentService
from app.services.sales_service import SalesService


def test_payment_accepts_partial_payments(app, inventory_context):
    _, store, product = inventory_context
    sale = SalesService().create_sale(
        [{"product_id": product.id, "quantity": "1", "unit_price": "1000"}],
        store_id=store.id,
    )
    service = PaymentService()
    first = service.add_payment(sale.id, "400", "cash")
    second = service.add_payment(sale.id, "600", "card")
    db.session.commit()
    assert first.amount == Decimal("400")
    assert second.amount == Decimal("600")
    assert Payment.query.filter_by(sale_id=sale.id, status="confirmed").count() == 2


def test_payment_cannot_exceed_sale_total(app, inventory_context):
    _, store, product = inventory_context
    sale = SalesService().create_sale(
        [{"product_id": product.id, "quantity": "1", "unit_price": "1000"}],
        store_id=store.id,
    )
    with pytest.raises(ValueError, match="exceeds sale total"):
        PaymentService().add_payment(sale.id, "1001", "cash")
    db.session.rollback()


def test_refund_restores_stock_and_marks_payments(app, inventory_context):
    _, store, product = inventory_context
    sale = SalesService().create_sale(
        [{"product_id": product.id, "quantity": "2", "unit_price": "1000"}],
        store_id=store.id,
    )
    PaymentService().add_payment(sale.id, "2000", "cash")
    PaymentService().refund_sale(sale.id)
    db.session.commit()

    stock = ProductStock.query.filter_by(product_id=product.id, store_id=store.id).one()
    assert stock.quantity == Decimal("0")
    assert sale.status == "refunded"
    assert Payment.query.filter_by(sale_id=sale.id, status="refunded").count() == 1
    returns = StockMovement.query.filter_by(
        reference_id=sale.id, reference_type="sale_refund"
    ).all()
    assert sum((m.quantity for m in returns), Decimal("0")) == Decimal("2")


def test_refund_is_idempotency_protected(app, inventory_context):
    _, store, product = inventory_context
    sale = SalesService().create_sale(
        [{"product_id": product.id, "quantity": "1"}], store_id=store.id
    )
    PaymentService().refund_sale(sale.id)
    with pytest.raises(ValueError, match="already refunded"):
        PaymentService().refund_sale(sale.id)
    db.session.rollback()
