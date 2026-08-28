"""Integration tests for SaaS billing rules."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.models import BillingPayment, Invoice, Plan, db
from app.services.billing_service import BillingService


def test_period_end_monthly():
    start = datetime(2026, 8, 28, tzinfo=timezone.utc)
    assert BillingService._period_end(start, "monthly") == datetime(
        2026, 9, 27, tzinfo=timezone.utc
    )


def test_period_end_yearly():
    start = datetime(2026, 8, 28, tzinfo=timezone.utc)
    assert BillingService._period_end(start, "yearly") == datetime(
        2027, 8, 28, tzinfo=timezone.utc
    )


def test_period_end_rejects_unknown_interval():
    with pytest.raises(ValueError, match="Unsupported billing interval"):
        BillingService._period_end(datetime.now(timezone.utc), "weekly")


def test_organization_id_requires_tenant_context(app, monkeypatch):
    monkeypatch.setattr(
        "app.services.billing_service.get_current_organization", lambda: None
    )
    with pytest.raises(ValueError, match="No current organization"):
        BillingService()._organization_id()


def _plan(price=10000, trial_days=14):
    plan = Plan(
        code="STARTER",
        name="Starter",
        monthly_price=Decimal(str(price)),
        yearly_price=Decimal(str(price * 10)),
        trial_days=trial_days,
        active=True,
    )
    db.session.add(plan)
    db.session.commit()
    return plan


def test_create_subscription_with_trial(app, tenant):
    plan = _plan()
    subscription = BillingService().create_subscription("STARTER")
    assert subscription.organization_id == tenant.id
    assert subscription.status == "trialing"
    assert subscription.trial_ends_at is not None
    assert subscription.plan_id == plan.id


def test_create_subscription_without_trial_is_active(app, tenant):
    _plan(trial_days=0)
    subscription = BillingService().create_subscription("STARTER", trial=False)
    assert subscription.status == "active"
    assert subscription.trial_ends_at is None


def test_create_subscription_rejects_invalid_plan_and_interval(app, tenant):
    service = BillingService()
    with pytest.raises(ValueError, match="Active plan not found"):
        service.create_subscription("MISSING")
    with pytest.raises(ValueError, match="Unsupported billing interval"):
        service.create_subscription("MISSING", interval="weekly")


def test_create_subscription_rejects_duplicate(app, tenant):
    _plan()
    service = BillingService()
    service.create_subscription("STARTER", trial=False)
    with pytest.raises(ValueError, match="already has an active subscription"):
        service.create_subscription("STARTER")
    db.session.rollback()


def test_cancel_subscription(app, tenant):
    _plan()
    service = BillingService()
    subscription = service.create_subscription("STARTER", trial=False)
    canceled = service.cancel_subscription(subscription.id)
    assert canceled.status == "canceled"
    assert canceled.canceled_at is not None


def test_cancel_subscription_rejects_missing_and_already_canceled(app, tenant):
    _plan()
    service = BillingService()
    with pytest.raises(ValueError, match="Subscription not found"):
        service.cancel_subscription(99999)
    subscription = service.create_subscription("STARTER", trial=False)
    service.cancel_subscription(subscription.id)
    with pytest.raises(ValueError, match="already inactive"):
        service.cancel_subscription(subscription.id)
    db.session.rollback()


def test_create_invoice_uses_monthly_price(app, tenant):
    _plan(price=12500)
    subscription = BillingService().create_subscription("STARTER", trial=False)
    invoice = BillingService().create_invoice(subscription.id, "INV-001")
    assert invoice.amount == Decimal("12500")
    assert invoice.status == "open"
    assert invoice.currency == "XOF"


def test_create_invoice_rejects_non_billable_subscription(app, tenant):
    _plan()
    service = BillingService()
    subscription = service.create_subscription("STARTER", trial=False)
    service.cancel_subscription(subscription.id)
    with pytest.raises(ValueError, match="Subscription is not billable"):
        service.create_invoice(subscription.id, "INV-002")
    db.session.rollback()


def test_record_partial_then_full_payment_marks_invoice_paid(app, tenant):
    _plan(price=10000)
    service = BillingService()
    subscription = service.create_subscription("STARTER", trial=False)
    invoice = service.create_invoice(subscription.id, "INV-003")
    first = service.record_payment(
        invoice.id, "4000", provider="wave", provider_reference="P1"
    )
    assert first.status == "succeeded"
    assert db.session.get(Invoice, invoice.id).status == "open"
    service.record_payment(invoice.id, "6000", provider="wave", provider_reference="P2")
    paid = db.session.get(Invoice, invoice.id)
    assert paid.status == "paid"
    assert paid.paid_at is not None
    assert BillingPayment.query.filter_by(invoice_id=invoice.id).count() == 2


def test_record_payment_rejects_invalid_amount_and_paid_invoice(app, tenant):
    _plan(price=1000)
    service = BillingService()
    subscription = service.create_subscription("STARTER", trial=False)
    invoice = service.create_invoice(subscription.id, "INV-004")
    with pytest.raises(ValueError, match="greater than zero"):
        service.record_payment(invoice.id, 0)
    service.record_payment(invoice.id, 1000)
    with pytest.raises(ValueError, match="already paid"):
        service.record_payment(invoice.id, 1)
    db.session.rollback()
