"""Payment and refund services for POS sales."""

from decimal import Decimal

from app.models import Payment, ProductBatch, Sale, StockMovement, db
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
        sale.payments.append(payment)
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

        sale_movements = StockMovement.query.filter_by(
            organization_id=organization_id,
            reference_type="sale",
            reference_id=sale.id,
            movement_type="sale",
        ).all()
        movements_by_product = {}
        for movement in sale_movements:
            movements_by_product.setdefault(movement.product_id, []).append(movement)

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

            prefix = "FEFO batch "
            for movement in movements_by_product.get(item.product_id, []):
                if not movement.note or not movement.note.startswith(prefix):
                    continue
                batch_id = int(movement.note[len(prefix):])
                batch = ProductBatch.query.filter_by(
                    id=batch_id,
                    product_id=item.product_id,
                    store_id=sale.store_id,
                    organization_id=organization_id,
                ).with_for_update().first()
                if batch is None:
                    raise ValueError("Original sale batch not found for refund")
                batch.quantity += abs(Decimal(str(movement.quantity)))

        sale.status = "refunded"
        for payment in sale.payments:
            if payment.status == "confirmed":
                payment.status = "refunded"
        db.session.flush()
        return sale
