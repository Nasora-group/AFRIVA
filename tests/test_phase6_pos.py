"""Coverage tests for Phase 6 POS business rules."""

from decimal import Decimal

import pytest

from app.models import POSRegister, Product, Store, db
from app.services.pos_service import POSValidationError, close_session, create_pos_sale, money, open_session


def pos_setup(tenant):
    store = Store(organization_id=tenant.id, name="Main Store", code="MAIN")
    db.session.add(store)
    db.session.flush()
    register = POSRegister(
        organization_id=tenant.id,
        store_id=store.id,
        name="Register 1",
        code="REG-1",
    )
    product = Product(
        organization_id=tenant.id,
        name="Test Product",
        sku="TEST-1",
        unit_price=Decimal("12.50"),
    )
    db.session.add_all([register, product])
    db.session.commit()
    return store, register, product


def test_money_validates_and_quantizes_values():
    assert money("12.345") == Decimal("12.35")
    assert money(0) == Decimal("0.00")
    with pytest.raises(POSValidationError, match="valid number"):
        money("abc")
    with pytest.raises(POSValidationError, match="non-negative"):
        money("-1")


def test_open_and_close_session(tenant):
    _, register, _ = pos_setup(tenant)
    session = open_session(
        organization_id=tenant.id, register_id=register.id, user_id=1, opening_cash="100"
    )
    assert session.status == "open"
    with pytest.raises(POSValidationError, match="already has an open session"):
        open_session(
            organization_id=tenant.id, register_id=register.id, user_id=1, opening_cash="50"
        )
    closed = close_session(
        organization_id=tenant.id, session_id=session.id, user_id=1, closing_cash="125.50"
    )
    assert closed.status == "closed"
    assert closed.closing_cash == Decimal("125.50")


def test_create_pos_sale_with_multiple_payments(tenant):
    _, register, product = pos_setup(tenant)
    session = open_session(
        organization_id=tenant.id, register_id=register.id, user_id=1, opening_cash="50"
    )
    sale = create_pos_sale(
        organization_id=tenant.id,
        session_id=session.id,
        lines=[{"product_id": product.id, "quantity": 2}],
        payments=[
            {"method": "cash", "amount": "10"},
            {"method": "card", "amount": "15"},
        ],
    )
    assert sale.total_amount == Decimal("25.00")
    assert len(sale.lines) == 1
    assert len(sale.payments) == 2


def test_create_pos_sale_rejects_invalid_input(tenant):
    _, register, product = pos_setup(tenant)
    session = open_session(
        organization_id=tenant.id, register_id=register.id, user_id=1, opening_cash="0"
    )
    with pytest.raises(POSValidationError, match="At least one"):
        create_pos_sale(organization_id=tenant.id, session_id=session.id, lines=[])
    with pytest.raises(POSValidationError, match="quantity"):
        create_pos_sale(
            organization_id=tenant.id,
            session_id=session.id,
            lines=[{"product_id": product.id, "quantity": 0}],
        )
    with pytest.raises(POSValidationError, match="Invalid payment"):
        create_pos_sale(
            organization_id=tenant.id,
            session_id=session.id,
            lines=[{"product_id": product.id, "quantity": 1}],
            payments=[{"method": "bitcoin", "amount": "12.50"}],
        )
