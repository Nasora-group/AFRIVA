"""Business rules for AFRIVA SaaS subscriptions and billing."""

from datetime import timedelta
from decimal import Decimal

from app.middleware.tenant_middleware import get_current_organization
from app.models import BillingPayment, Invoice, Plan, Subscription, db
from app.models.base import utcnow


class BillingService:
    """Tenant-aware billing operations."""

    def _organization_id(self):
        organization = get_current_organization()
        if organization is None:
            raise ValueError("No current organization")
        return organization.id

    @staticmethod
    def _period_end(start, interval):
        if interval == "monthly":
            return start + timedelta(days=30)
        if interval == "yearly":
            return start + timedelta(days=365)
        raise ValueError("Unsupported billing interval")

    def create_subscription(self, plan_code, interval="monthly", trial=True):
        organization_id = self._organization_id()
        if interval not in {"monthly", "yearly"}:
            raise ValueError("Unsupported billing interval")
        plan = Plan.query.filter_by(code=plan_code, active=True).first()
        if plan is None:
            raise ValueError("Active plan not found")
        existing = Subscription.query.filter_by(
            organization_id=organization_id,
            status="active",
        ).first()
        trialing = Subscription.query.filter_by(
            organization_id=organization_id,
            status="trialing",
        ).first()
        if existing or trialing:
            raise ValueError("Organization already has an active subscription")
        now = utcnow()
        trial_ends = now + timedelta(days=plan.trial_days) if trial else None
        subscription = Subscription(
            organization_id=organization_id,
            plan_id=plan.id,
            status="trialing" if trial and plan.trial_days > 0 else "active",
            billing_interval=interval,
            started_at=now,
            trial_ends_at=trial_ends,
            current_period_start=now,
            current_period_end=self._period_end(now, interval),
        )
        db.session.add(subscription)
        db.session.flush()
        return subscription

    def cancel_subscription(self, subscription_id):
        organization_id = self._organization_id()
        subscription = Subscription.query.filter_by(
            id=subscription_id, organization_id=organization_id
        ).first()
        if subscription is None:
            raise ValueError("Subscription not found")
        if subscription.status in {"canceled", "expired"}:
            raise ValueError("Subscription is already inactive")
        subscription.status = "canceled"
        subscription.canceled_at = utcnow()
        db.session.flush()
        return subscription

    def create_invoice(self, subscription_id, number, due_at=None):
        organization_id = self._organization_id()
        subscription = Subscription.query.filter_by(
            id=subscription_id, organization_id=organization_id
        ).first()
        if subscription is None:
            raise ValueError("Subscription not found")
        if subscription.status not in {"active", "trialing"}:
            raise ValueError("Subscription is not billable")
        amount = Decimal(str(
            subscription.plan.monthly_price
            if subscription.billing_interval == "monthly"
            else subscription.plan.yearly_price
        ))
        invoice = Invoice(
            organization_id=organization_id,
            subscription_id=subscription.id,
            number=number,
            amount=amount,
            currency="XOF",
            due_at=due_at,
        )
        db.session.add(invoice)
        db.session.flush()
        return invoice

    def record_payment(self, invoice_id, amount, provider="manual", provider_reference=None):
        organization_id = self._organization_id()
        invoice = Invoice.query.filter_by(
            id=invoice_id, organization_id=organization_id
        ).first()
        if invoice is None:
            raise ValueError("Invoice not found")
        payment_amount = Decimal(str(amount))
        if payment_amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        if invoice.status == "paid":
            raise ValueError("Invoice is already paid")
        payment = BillingPayment(
            organization_id=organization_id,
            invoice_id=invoice.id,
            amount=payment_amount,
            currency=invoice.currency,
            status="succeeded",
            provider=provider,
            provider_reference=provider_reference,
            paid_at=utcnow(),
        )
        db.session.add(payment)
        db.session.flush()
        paid_total = sum(
            (Decimal(str(p.amount)) for p in BillingPayment.query.filter_by(
                invoice_id=invoice.id, organization_id=organization_id, status="succeeded"
            ).all()),
            Decimal("0"),
        )
        if paid_total >= Decimal(str(invoice.amount)):
            invoice.status = "paid"
            invoice.paid_at = payment.paid_at
        db.session.flush()
        return payment
