"""Payment and refund services for POS sales."""

from decimal import Decimal

from app.models import Payment, Sale, StockMovement, db
from app.services.inventory_service import InventoryService


class PaymentService:
    def __init__(self):
        self.inventory = InventoryService()

    def add_payment(self, sale_id, amount, method, reference=None, cash_session_id=None):
        organization_id = self.inventory._organization_id()
        sale = Sale.query.filter_by(id=sale_id, organization_id=organization_id).first()
        if sale is None:
            raise ValueError("Sale not found in current organization")
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        paid = sum(
            (p.amount for p in sale.payments if p.status == "confirmed"), Decimal("0")
        )
        if paid + amount > sale.total_amount:
            raise ValueError("Payment exceeds sale total")
        payment = Payment(
            organization_id=organization_id,
            sale_id=sale.id,
            cash_session_id=cash_session_id,
            method=method,
            amount=amount,
            reference=reference,
            status="confirmed",
        )
        db.session.add(payment)
        db.session.flush()
        return payment

    def refund_sale(self, sale_id):
        organization_id = self.inventory._organization_id()
        sale = Sale.query.filter_by(id=sale_id, organization_id=organization_id).first()
        if sale is None:
            raise ValueError("Sale not found in current organization")
        if sale.status == "refunded":
            raise ValueError("Sale is already refunded")
        if sale.status != "confirmed":
            raise ValueError("Only confirmed sales can be refunded")
        for item in sale.items:
            self.inventory.adjust_stock(
                product_id=item.product_id,
                store_id=sale.store_id,
                quantity=item.quantity,
                movement_type="return",
                reference_type="sale_refund",
                reference_id=sale.id,
                note="POS sale refund",
            )
        sale.status = "refunded"
        for payment in sale.payments:
            if payment.status == "confirmed":
                payment.status = "refunded"
        db.session.add(
            StockMovement(
                organization_id=organization_id,
                product_id=sale.items[0].product_id if sale.items else 0,
                store_id=sale.store_id,
                movement_type="return",
                quantity=Decimal("0"),
                reference_type="sale_refund",
                reference_id=sale.id,
                note="Refund completed",
            )
        )
        db.session.flush()
        return sale
