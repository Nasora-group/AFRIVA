"""Business rules for AFRIVA SaaS subscriptions and billing."""

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

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

    @staticmethod
    def _money(value):
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("Amount must be a valid number") from exc
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        return amount

    def create_subscription(self, plan_code, interval="monthly", trial=True):
        organization_id = self._organization_id()
        if interval not in {"monthly", "yearly"}:
            raise ValueError("Unsupported billing interval")
        plan = Plan.query.filter_by(code=plan_code, active=True).first()
        if plan is None:
            raise ValueError("Active plan not found")
        existing = Subscription.query.filter_by(
            organization_id=organization_id, status="active"
        ).first()
        trialing = Subscription.query.filter_by(
            organization_id=organization_id, status="trialing"
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

    def refresh_subscription_status(self, subscription=None):
        """Expire trial or period when its contractual end is reached."""
        organization_id = self._organization_id()
        if subscription is None:
            subscription = (
                Subscription.query.filter_by(
                    organization_id=organization_id, status="trialing"
                ).first()
                or Subscription.query.filter_by(
                    organization_id=organization_id, status="active"
                ).first()
            )
        if subscription is None:
            return None
        now = utcnow()
        changed = False
        if (
            subscription.status == "trialing"
            and subscription.trial_ends_at
            and now >= subscription.trial_ends_at
        ):
            subscription.status = "expired"
            changed = True
        elif (
            subscription.status == "active"
            and subscription.current_period_end
            and now >= subscription.current_period_end
        ):
            subscription.status = "expired"
            changed = True
        if changed:
            db.session.flush()
        return subscription

    def change_plan(self, plan_code, interval="monthly", trial=False):
        """Change the current tenant plan and start a fresh billing period."""
        organization_id = self._organization_id()
        if interval not in {"monthly", "yearly"}:
            raise ValueError("Unsupported billing interval")
        plan = Plan.query.filter_by(code=plan_code, active=True).first()
        if plan is None:
            raise ValueError("Active plan not found")
        subscription = (
            Subscription.query.filter_by(
                organization_id=organization_id, status="active"
            ).first()
            or Subscription.query.filter_by(
                organization_id=organization_id, status="trialing"
            ).first()
        )
        if subscription is None:
            return self.create_subscription(plan_code, interval, trial)
        now = utcnow()
        subscription.plan_id = plan.id
        subscription.billing_interval = interval
        subscription.status = "trialing" if trial and plan.trial_days > 0 else "active"
        subscription.trial_ends_at = now + timedelta(days=plan.trial_days) if subscription.status == "trialing" else None
        subscription.current_period_start = now
        subscription.current_period_end = self._period_end(now, interval)
        subscription.canceled_at = None
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
        if not number or not str(number).strip():
            raise ValueError("Invoice number is required")
        subscription = Subscription.query.filter_by(
            id=subscription_id, organization_id=organization_id
        ).first()
        if subscription is None:
            raise ValueError("Subscription not found")
        if subscription.status not in {"active", "trialing"}:
            raise ValueError("Subscription is not billable")
        if isinstance(due_at, str):
            try:
                due_at = datetime.fromisoformat(due_at.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError("due_at must be a valid ISO-8601 datetime") from exc
        price = (
            subscription.plan.monthly_price
            if subscription.billing_interval == "monthly"
            else subscription.plan.yearly_price
        )
        invoice = Invoice(
            organization_id=organization_id,
            subscription_id=subscription.id,
            number=str(number).strip(),
            amount=Decimal(str(price)),
            currency="XOF",
            due_at=due_at,
        )
        db.session.add(invoice)
        db.session.flush()
        return invoice

    def record_payment(
        self, invoice_id, amount, provider="manual", provider_reference=None
    ):
        organization_id = self._organization_id()
        invoice = Invoice.query.filter_by(
            id=invoice_id, organization_id=organization_id
        ).first()
        if invoice is None:
            raise ValueError("Invoice not found")
        payment_amount = self._money(amount)
        if invoice.status == "paid":
            raise ValueError("Invoice is already paid")
        payments = BillingPayment.query.filter_by(
            invoice_id=invoice.id,
            organization_id=organization_id,
            status="succeeded",
        ).all()
        paid_total = sum((Decimal(str(item.amount)) for item in payments), Decimal("0"))
        remaining = Decimal(str(invoice.amount)) - paid_total
        if payment_amount > remaining:
            raise ValueError("Payment exceeds invoice balance")
        payment = BillingPayment(
            organization_id=organization_id,
            invoice_id=invoice.id,
            amount=payment_amount,
            currency=invoice.currency,
            status="succeeded",
            provider=provider or "manual",
            provider_reference=provider_reference,
            paid_at=utcnow(),
        )
        db.session.add(payment)
        db.session.flush()
        if paid_total + payment_amount == Decimal(str(invoice.amount)):
            invoice.status = "paid"
            invoice.paid_at = payment.paid_at
        return payment
