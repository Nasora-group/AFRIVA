from decimal import Decimal

import pytest

from app.models import BillingPayment, Invoice, Organization, Plan, Subscription, db
from app.services.billing_service import BillingService


def _billing_context(app, monkeypatch):
    organization = Organization(name="Billing Org", slug="billing-org")
    plan = Plan(
        code="starter",
        name="Starter",
        monthly_price=Decimal("10000"),
        yearly_price=Decimal("100000"),
        trial_days=14,
        max_users=5,
        max_stores=2,
        max_products=100,
    )
    db.session.add_all([organization, plan])
    db.session.commit()
    monkeypatch.setattr(
        "app.services.billing_service.get_current_organization", lambda: organization
    )
    return organization, plan


def test_billing_subscription_invoice_payment_lifecycle(app, monkeypatch):
    organization, plan = _billing_context(app, monkeypatch)
    service = BillingService()

    subscription = service.create_subscription("starter", trial=True)
    db.session.commit()
    assert subscription.organization_id == organization.id
    assert subscription.status == "trialing"
    assert subscription.trial_ends_at is not None

    invoice = service.create_invoice(subscription.id, "INV-0001")
    db.session.commit()
    assert invoice.amount == Decimal("10000.00")
    assert invoice.currency == "XOF"
    assert invoice.status == "open"

    payment = service.record_payment(invoice.id, "10000", provider="manual")
    db.session.commit()
    assert payment.status == "succeeded"
    assert Invoice.query.get(invoice.id).status == "paid"
    assert BillingPayment.query.count() == 1
    assert plan.id == subscription.plan_id


def test_billing_partial_payment_and_balance(app, monkeypatch):
    _billing_context(app, monkeypatch)
    service = BillingService()
    subscription = service.create_subscription("starter", trial=False)
    db.session.commit()
    invoice = service.create_invoice(subscription.id, "INV-0002")
    db.session.commit()

    service.record_payment(invoice.id, "4000")
    db.session.commit()
    assert Invoice.query.get(invoice.id).status == "open"

    with pytest.raises(ValueError, match="exceeds invoice balance"):
        service.record_payment(invoice.id, "7000")

    service.record_payment(invoice.id, "6000")
    db.session.commit()
    assert Invoice.query.get(invoice.id).status == "paid"


def test_billing_rejects_second_active_subscription(app, monkeypatch):
    _billing_context(app, monkeypatch)
    service = BillingService()
    service.create_subscription("starter", trial=False)
    db.session.commit()

    with pytest.raises(ValueError, match="already has an active subscription"):
        service.create_subscription("starter", trial=False)


def test_billing_is_tenant_scoped(app, monkeypatch):
    organization, _ = _billing_context(app, monkeypatch)
    other = Organization(name="Other Org", slug="other-billing-org")
    db.session.add(other)
    db.session.commit()

    service = BillingService()
    subscription = service.create_subscription("starter", trial=False)
    db.session.commit()

    monkeypatch.setattr(
        "app.services.billing_service.get_current_organization", lambda: other
    )
    with pytest.raises(ValueError, match="Subscription not found"):
        service.cancel_subscription(subscription.id)

    assert Subscription.query.filter_by(organization_id=organization.id).count() == 1
