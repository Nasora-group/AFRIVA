"""Business services for tenant-safe sales operations."""

from decimal import Decimal, InvalidOperation

from app.models import Client, Commercial, Product, Sale, SaleLine, SalesTarget, db


class SalesValidationError(ValueError):
    """Raised when a sales payload is invalid."""


def _decimal(value, field):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise SalesValidationError(f"{field} must be a valid number") from exc
    if number < 0:
        raise SalesValidationError(f"{field} must be non-negative")
    return number


def create_sale(
    *,
    organization_id,
    commercial_id,
    client_id=None,
    lines,
    status="confirmed",
    notes=None,
):
    if not lines:
        raise SalesValidationError("At least one sale line is required")

    commercial = Commercial.query.filter_by(
        id=commercial_id,
        organization_id=organization_id,
        deleted_at=None,
    ).first()
    if commercial is None:
        raise SalesValidationError("Commercial not found in current organization")

    client = None
    if client_id is not None:
        client = Client.query.filter_by(
            id=client_id,
            organization_id=organization_id,
            deleted_at=None,
        ).first()
        if client is None:
            raise SalesValidationError("Client not found in current organization")

    if status not in {"draft", "confirmed", "cancelled"}:
        raise SalesValidationError("Invalid sale status")

    sale = Sale(
        organization_id=organization_id,
        commercial=commercial,
        client=client,
        status=status,
        notes=notes,
    )
    for item in lines:
        if not isinstance(item, dict):
            raise SalesValidationError("Each line must be an object")
        product_id = item.get("product_id")
        product = Product.query.filter_by(
            id=product_id,
            organization_id=organization_id,
            deleted_at=None,
            active=True,
        ).first()
        if product is None:
            raise SalesValidationError("Product not found in current organization")
        quantity = _decimal(item.get("quantity", 1), "quantity")
        if quantity <= 0:
            raise SalesValidationError("quantity must be greater than zero")
        unit_price = _decimal(item.get("unit_price", product.unit_price), "unit_price")
        line = SaleLine(
            organization_id=organization_id,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
        )
        line.calculate_total()
        sale.lines.append(line)

    sale.recalculate_total()
    db.session.add(sale)
    db.session.commit()
    return sale


def set_sales_target(*, organization_id, commercial_id, year, month, target_amount):
    try:
        year = int(year)
        month = int(month)
    except (TypeError, ValueError) as exc:
        raise SalesValidationError("year and month must be integers") from exc
    if not 1 <= month <= 12:
        raise SalesValidationError("month must be between 1 and 12")

    commercial = Commercial.query.filter_by(
        id=commercial_id,
        organization_id=organization_id,
        deleted_at=None,
    ).first()
    if commercial is None:
        raise SalesValidationError("Commercial not found in current organization")

    amount = _decimal(target_amount, "target_amount")
    target = SalesTarget.query.filter_by(
        organization_id=organization_id,
        commercial_id=commercial_id,
        year=year,
        month=month,
    ).first()
    if target is None:
        target = SalesTarget(
            organization_id=organization_id,
            commercial_id=commercial_id,
            year=year,
            month=month,
            target_amount=amount,
        )
        db.session.add(target)
    else:
        target.target_amount = amount
    db.session.commit()
    return target
