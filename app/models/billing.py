"""SaaS billing models."""

from decimal import Decimal

from .base import BaseModel, TenantAwareModel, db, utcnow


class Plan(BaseModel):
    __tablename__ = "billing_plan"

    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    monthly_price = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0"))
    yearly_price = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0"))
    trial_days = db.Column(db.Integer, nullable=False, default=14)
    max_users = db.Column(db.Integer, nullable=True)
    max_stores = db.Column(db.Integer, nullable=True)
    max_products = db.Column(db.Integer, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)


class Subscription(TenantAwareModel):
    __tablename__ = "billing_subscription"

    plan_id = db.Column(
        db.Integer,
        db.ForeignKey("billing_plan.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status = db.Column(db.String(30), nullable=False, default="trialing", index=True)
    billing_interval = db.Column(db.String(20), nullable=False, default="monthly")
    started_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    trial_ends_at = db.Column(db.DateTime(timezone=True), nullable=True)
    current_period_start = db.Column(
        db.DateTime(timezone=True), default=utcnow, nullable=False
    )
    current_period_end = db.Column(db.DateTime(timezone=True), nullable=False)
    canceled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    external_customer_id = db.Column(db.String(255), nullable=True)
    external_subscription_id = db.Column(
        db.String(255), unique=True, nullable=True
    )

    plan = db.relationship("Plan")


class Invoice(TenantAwareModel):
    __tablename__ = "billing_invoice"

    subscription_id = db.Column(
        db.Integer,
        db.ForeignKey("billing_subscription.id", ondelete="RESTRICT"),
        nullable=False,
    )
    number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="open", index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="XOF")
    issued_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    due_at = db.Column(db.DateTime(timezone=True), nullable=True)
    paid_at = db.Column(db.DateTime(timezone=True), nullable=True)

    subscription = db.relationship("Subscription")


class BillingPayment(TenantAwareModel):
    __tablename__ = "billing_payment"

    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("billing_invoice.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="XOF")
    status = db.Column(db.String(30), nullable=False, default="pending", index=True)
    provider = db.Column(db.String(50), nullable=False, default="manual")
    provider_reference = db.Column(db.String(255), unique=True, nullable=True)
    paid_at = db.Column(db.DateTime(timezone=True), nullable=True)

    invoice = db.relationship("Invoice")
