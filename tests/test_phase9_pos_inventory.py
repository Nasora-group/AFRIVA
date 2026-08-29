from decimal import Decimal

import pytest

from app.models import CashSession, POSRegister, Product, ProductStock, Store, User, db
from app.services.pos_service import POSValidationError, create_pos_sale, open_session


def test_pos_sale_consumes_store_stock(app, tenant):
    user = User(email="cashier@example.com", password_hash="test")
    store = Store(
        organization_id=tenant.id,
        name="Dakar Store",
        code="DKR",
        active=True,
    )
    register = POSRegister(
        organization_id=tenant.id,
        store=store,
        name="Caisse 1",
        code="C1",
        active=True,
    )
    product = Product(
        organization_id=tenant.id,
        name="POS Product",
        sku="POS-001",
        unit_price=Decimal("1000.00"),
        active=True,
    )
    db.session.add_all([user, store, register, product])
    db.session.flush()
    db.session.add(
        ProductStock(
            organization_id=tenant.id,
            product_id=product.id,
            store_id=store.id,
            quantity=Decimal("10"),
        )
    )
    db.session.commit()

    session = open_session(
        organization_id=tenant.id,
        register_id=register.id,
        user_id=user.id,
        opening_cash=Decimal("0"),
    )
    sale = create_pos_sale(
        organization_id=tenant.id,
        session_id=session.id,
        lines=[{"product_id": product.id, "quantity": "3"}],
        payments=[{"method": "cash", "amount": "3000"}],
    )

    stock = ProductStock.query.filter_by(
        organization_id=tenant.id, product_id=product.id, store_id=store.id
    ).one()
    assert sale.total_amount == Decimal("3000.00")
    assert stock.quantity == Decimal("7")


def test_pos_sale_rejects_insufficient_stock_without_sale(app, tenant):
    user = User(email="cashier2@example.com", password_hash="test")
    store = Store(
        organization_id=tenant.id, name="Touba Store", code="TOU", active=True
    )
    register = POSRegister(
        organization_id=tenant.id,
        store=store,
        name="Caisse 1",
        code="C1",
        active=True,
    )
    product = Product(
        organization_id=tenant.id,
        name="Limited Product",
        sku="POS-002",
        unit_price=Decimal("500.00"),
        active=True,
    )
    db.session.add_all([user, store, register, product])
    db.session.flush()
    db.session.add(
        ProductStock(
            organization_id=tenant.id,
            product_id=product.id,
            store_id=store.id,
            quantity=Decimal("1"),
        )
    )
    db.session.commit()

    session = open_session(
        organization_id=tenant.id,
        register_id=register.id,
        user_id=user.id,
        opening_cash=Decimal("0"),
    )
    with pytest.raises(POSValidationError, match="Insufficient stock"):
        create_pos_sale(
            organization_id=tenant.id,
            session_id=session.id,
            lines=[{"product_id": product.id, "quantity": "2"}],
            payments=[{"method": "cash", "amount": "1000"}],
        )

    db.session.rollback()
    assert CashSession.query.filter_by(id=session.id).one().status == "open"
    assert ProductStock.query.filter_by(
        organization_id=tenant.id, product_id=product.id, store_id=store.id
    ).one().quantity == Decimal("1")
