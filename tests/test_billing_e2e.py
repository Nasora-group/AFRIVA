from decimal import Decimal

from app.models import BillingPayment, Invoice, Plan, Subscription, db
from app.services.billing_service import BillingService


def test_billing_lifecycle_and_tenant_isolation(app, inventory_context, monkeypatch):
    organization = inventory_context[0]
    other_organization = type(organization)(name="Other Org")
    db.session.add(other_organization)
    db.session.flush()
    plan = Plan(
        code="e2e",
        name="E2E",
        description="Billing test plan",
        monthly_price=Decimal("10000"),
        yearly_price=Decimal("100000"),
        trial_days=0,
        max_users=10,
        max_stores=2,
        max_products=100,
        active=True,
    )
    db.session.add(plan)
    db.session.commit()
    monkeypatch.setattr(
        "app.services.billing_service.get_current_organization", lambda: organization
    )

    service = BillingService()
    subscription = service.create_subscription("e2e", trial=False)
    db.session.commit()
    invoice = service.create_invoice(subscription.id, "E2E-001")
    db.session.commit()

    payment = service.record_payment(invoice.id, "4000")
    db.session.commit()
    assert payment.status == "succeeded"
    assert Invoice.query.get(invoice.id).status != "paid"

    service.record_payment(invoice.id, "6000")
    db.session.commit()
    assert Invoice.query.get(invoice.id).status == "paid"

    try:
        service.record_payment(invoice.id, "1")
    except ValueError as exc:
        assert "already paid" in str(exc)
    else:
        raise AssertionError("A paid invoice accepted another payment")

    monkeypatch.setattr(
        "app.services.billing_service.get_current_organization",
        lambda: other_organization,
    )
    try:
        service.cancel_subscription(subscription.id)
    except ValueError as exc:
        assert "not found" in str(exc)
    else:
        raise AssertionError("Cross-tenant subscription access was allowed")
