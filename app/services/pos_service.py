"""Business rules for POS and cash sessions."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from app.models import (
    CashSession,
    POSPayment,
    POSRegister,
    POSSale,
    POSSaleLine,
    Product,
    ProductBatch,
    ProductStock,
    StockMovement,
    Store,
    db,
)


class POSValidationError(ValueError):
    """Raised when a POS operation is invalid."""


def money(value, field="amount"):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise POSValidationError(f"{field} must be a valid number") from exc
    if result < 0:
        raise POSValidationError(f"{field} must be non-negative")
    return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def open_session(*, organization_id, register_id, user_id, opening_cash):
    register = (
        POSRegister.query.join(Store)
        .filter(
            POSRegister.id == register_id,
            POSRegister.organization_id == organization_id,
            POSRegister.active.is_(True),
            Store.organization_id == organization_id,
            Store.active.is_(True),
            POSRegister.store_id == Store.id,
        )
        .first()
    )
    if register is None:
        raise POSValidationError("Register not found in current organization")
    existing = CashSession.query.filter_by(
        organization_id=organization_id, register_id=register_id, status="open"
    ).first()
    if existing:
        raise POSValidationError("Register already has an open session")
    session = CashSession(
        organization_id=organization_id,
        register_id=register_id,
        opened_by=user_id,
        opening_cash=money(opening_cash, "opening_cash"),
    )
    db.session.add(session)
    db.session.commit()
    return session


def _consume_inventory(organization_id, store_id, product_id, quantity, sale_id=None):
    """Decrease store stock and consume non-expired batches FEFO, atomically."""
    stock = (
        ProductStock.query.filter_by(
            organization_id=organization_id,
            store_id=store_id,
            product_id=product_id,
        )
        .with_for_update()
        .first()
    )
    if stock is None or Decimal(str(stock.quantity)) < quantity:
        raise POSValidationError("Insufficient stock for POS sale")

    batches = (
        ProductBatch.query.filter(
            ProductBatch.organization_id == organization_id,
            ProductBatch.store_id == store_id,
            ProductBatch.product_id == product_id,
            ProductBatch.quantity > 0,
            db.or_(
                ProductBatch.expiry_date.is_(None),
                ProductBatch.expiry_date >= db.func.current_date(),
            ),
        )
        .order_by(ProductBatch.expiry_date.asc().nullslast(), ProductBatch.id.asc())
        .with_for_update()
        .all()
    )
    batch_total = sum((Decimal(str(batch.quantity)) for batch in batches), Decimal("0"))
    if batches and batch_total < quantity:
        raise POSValidationError("Insufficient non-expired batch stock for POS sale")

    stock.quantity = Decimal(str(stock.quantity)) - quantity
    remaining = quantity
    for batch in batches:
        if remaining <= 0:
            break
        taken = min(Decimal(str(batch.quantity)), remaining)
        batch.quantity -= taken
        remaining -= taken

    if sale_id is not None:
        db.session.add(
            StockMovement(
                organization_id=organization_id,
                product_id=product_id,
                store_id=store_id,
                movement_type="OUT",
                quantity=quantity,
                reference_type="POS",
                reference_id=sale_id,
                note="POS sale stock consumption",
            )
        )


def create_pos_sale(*, organization_id, session_id, lines, payments=None):
    session = CashSession.query.filter_by(
        id=session_id, organization_id=organization_id, status="open"
    ).first()
    if session is None:
        raise POSValidationError("Open cash session not found")
    if not lines:
        raise POSValidationError("At least one POS sale line is required")
    sale = POSSale(
        organization_id=organization_id,
        session=session,
        reference=(
            f"POS-{session.id}-"
            f"{POSSale.query.filter_by(organization_id=organization_id).count() + 1}"
        ),
        status="confirmed",
    )
    db.session.add(sale)
    db.session.flush()
    total = Decimal("0")
    for item in lines:
        product = Product.query.filter_by(
            id=item.get("product_id"),
            organization_id=organization_id,
            deleted_at=None,
            active=True,
        ).first()
        if product is None:
            raise POSValidationError("Product not found in current organization")
        quantity = Decimal(str(item.get("quantity", 1)))
        if quantity <= 0:
            raise POSValidationError("quantity must be greater than zero")
        price = money(item.get("unit_price", product.unit_price), "unit_price")
        line_total = (quantity * price).quantize(Decimal("0.01"))
        sale.lines.append(
            POSSaleLine(
                organization_id=organization_id,
                product=product,
                quantity=quantity,
                unit_price=price,
                line_total=line_total,
            )
        )
        _consume_inventory(
            organization_id,
            session.register.store_id,
            product.id,
            quantity,
            sale.id,
        )
        total += line_total
    sale.total_amount = total
    payment_total = Decimal("0")
    for item in payments or []:
        amount = money(item.get("amount"), "payment amount")
        if amount <= 0:
            raise POSValidationError("payment amount must be greater than zero")
        if item.get("method") not in {"cash", "card", "mobile_money", "transfer"}:
            raise POSValidationError("Invalid payment method")
        sale.payments.append(
            POSPayment(
                organization_id=organization_id,
                method=item["method"],
                amount=amount,
            )
        )
        payment_total += amount
    if payments and payment_total != total:
        raise POSValidationError("Payments must equal the sale total")
    db.session.commit()
    return sale


def close_session(*, organization_id, session_id, user_id, closing_cash):
    session = CashSession.query.filter_by(
        id=session_id, organization_id=organization_id, status="open"
    ).first()
    if session is None:
        raise POSValidationError("Open cash session not found")
    session.closing_cash = money(closing_cash, "closing_cash")
    session.closed_by = user_id
    session.closed_at = db.func.now()
    session.status = "closed"
    db.session.commit()
    return session
