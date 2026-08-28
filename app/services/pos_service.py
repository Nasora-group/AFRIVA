"""Business operations for POS cash sessions and checkout."""

from datetime import date
from decimal import Decimal, InvalidOperation

from app.middleware.tenant_middleware import get_current_organization
from app.models import CashRegister, CashSession, Payment, Product, Sale, SaleItem, db
from app.repositories.crm_repository import ClientRepository, CommercialRepository


PAYMENT_METHODS = {"cash", "card", "mobile_money", "bank_transfer", "check"}


class POSService:
    def _organization_id(self):
        organization = get_current_organization()
        if organization is None:
            raise ValueError("No current organization")
        return organization.id

    def open_session(self, register_id, opened_by, opening_amount=Decimal("0.00")):
        register = CashRegister.query.filter_by(id=register_id, active=True).first()
        if register is None:
            raise ValueError("Cash register not found in current organization")
        if opening_amount < 0:
            raise ValueError("opening_amount must be non-negative")
        existing = CashSession.query.filter_by(
            register_id=register_id, status="open"
        ).first()
        if existing is not None:
            raise ValueError("Cash register already has an open session")
        session = CashSession(
            register_id=register_id,
            opened_by=opened_by,
            opening_amount=opening_amount,
            status="open",
            organization_id=register.organization_id,
        )
        db.session.add(session)
        db.session.flush()
        return session

    def close_session(self, session_id, closed_by, closing_amount):
        session = CashSession.query.filter_by(id=session_id, status="open").first()
        if session is None:
            raise ValueError("Open cash session not found in current organization")
        closing_amount = Decimal(str(closing_amount))
        if closing_amount < 0:
            raise ValueError("closing_amount must be non-negative")
        session.closed_by = closed_by
        session.closing_amount = closing_amount
        session.closed_at = db.func.now()
        session.status = "closed"
        db.session.flush()
        return session

    def create_sale(
        self,
        session_id,
        items,
        payments,
        commercial_id=None,
        client_id=None,
        sale_date=None,
    ):
        organization_id = self._organization_id()
        session = CashSession.query.filter_by(
            id=session_id, organization_id=organization_id, status="open"
        ).first()
        if session is None:
            raise ValueError("Open cash session not found in current organization")
        if not items:
            raise ValueError("At least one sale item is required")
        if not payments:
            raise ValueError("At least one payment is required")

        if commercial_id is not None:
            commercial = CommercialRepository().get(commercial_id)
            if commercial is None:
                raise ValueError("Commercial not found in current organization")
        if client_id is not None:
            client = ClientRepository().get(client_id)
            if client is None:
                raise ValueError("Client not found in current organization")

        sale = Sale(
            organization_id=organization_id,
            cash_session_id=session.id,
            commercial_id=commercial_id,
            client_id=client_id,
            sale_date=sale_date or date.today(),
            status="confirmed",
            total_amount=Decimal("0.00"),
        )
        total = Decimal("0.00")

        for item in items:
            try:
                product_id = int(item["product_id"])
                quantity = Decimal(str(item["quantity"]))
                unit_price = Decimal(str(item.get("unit_price"))) if item.get("unit_price") is not None else None
            except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
                raise ValueError("Invalid sale item") from exc

            product = Product.query.filter_by(
                id=product_id, organization_id=organization_id, active=True
            ).first()
            if product is None:
                raise ValueError("Product not found in current organization")
            if quantity <= 0:
                raise ValueError("quantity must be greater than zero")
            if unit_price is None:
                unit_price = Decimal(str(product.unit_price))
            if unit_price < 0:
                raise ValueError("unit_price must be non-negative")

            line_total = (quantity * unit_price).quantize(Decimal("0.01"))
            sale.items.append(
                SaleItem(
                    organization_id=organization_id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total,
                )
            )
            total += line_total

        if total <= 0:
            raise ValueError("Sale total must be greater than zero")

        paid = Decimal("0.00")
        for payment in payments:
            method = str(payment.get("method", "")).strip().lower()
            try:
                amount = Decimal(str(payment["amount"])).quantize(Decimal("0.01"))
            except (KeyError, TypeError, ValueError, InvalidOperation) as exc:
                raise ValueError("Invalid payment amount") from exc
            if method not in PAYMENT_METHODS:
                raise ValueError("Unsupported payment method")
            if amount <= 0:
                raise ValueError("Payment amount must be greater than zero")
            sale.payments.append(
                Payment(
                    organization_id=organization_id,
                    cash_session_id=session.id,
                    method=method,
                    amount=amount,
                    reference=payment.get("reference"),
                    status="confirmed",
                )
            )
            paid += amount

        if paid != total:
            raise ValueError("Payment total must equal sale total")

        sale.total_amount = total
        db.session.add(sale)
        db.session.flush()
        return sale
