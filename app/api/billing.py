"""Tenant-aware SaaS billing endpoints."""

from flask import Blueprint, g, jsonify, request

from app.auth import login_required
from app.models import Invoice, Plan, Subscription, db
from app.services.billing_service import BillingService

billing_api = Blueprint("billing_api", __name__, url_prefix="/api/v1/billing")


def _plan_json(plan):
    return {
        "id": plan.id,
        "code": plan.code,
        "name": plan.name,
        "description": plan.description,
        "monthly_price": float(plan.monthly_price),
        "yearly_price": float(plan.yearly_price),
        "trial_days": plan.trial_days,
        "max_users": plan.max_users,
        "max_stores": plan.max_stores,
        "max_products": plan.max_products,
    }


@billing_api.get("/plans")
def plans():
    rows = Plan.query.filter_by(active=True).order_by(Plan.monthly_price, Plan.id).all()
    return jsonify({"items": [_plan_json(plan) for plan in rows]})


@billing_api.get("/subscription")
@login_required
def subscription():
    value = (
        Subscription.query.filter_by(
            organization_id=g.current_org_id, status="active"
        ).first()
        or Subscription.query.filter_by(
            organization_id=g.current_org_id, status="trialing"
        ).first()
    )
    if value is None:
        return jsonify({"subscription": None})
    return jsonify(
        {
            "subscription": {
                "id": value.id,
                "plan": value.plan.code,
                "status": value.status,
                "billing_interval": value.billing_interval,
                "trial_ends_at": value.trial_ends_at.isoformat()
                if value.trial_ends_at
                else None,
                "current_period_start": value.current_period_start.isoformat(),
                "current_period_end": value.current_period_end.isoformat(),
            }
        }
    )


@billing_api.post("/subscriptions")
@login_required
def create_subscription():
    payload = request.get_json(silent=True) or {}
    try:
        value = BillingService().create_subscription(
            plan_code=payload["plan_code"],
            interval=payload.get("interval", "monthly"),
            trial=bool(payload.get("trial", True)),
        )
        db.session.commit()
    except (KeyError, TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    return jsonify({"id": value.id, "status": value.status}), 201


@billing_api.post("/subscriptions/<int:subscription_id>/cancel")
@login_required
def cancel_subscription(subscription_id):
    try:
        value = BillingService().cancel_subscription(subscription_id)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    return jsonify({"id": value.id, "status": value.status})


@billing_api.post("/invoices")
@login_required
def create_invoice():
    payload = request.get_json(silent=True) or {}
    try:
        value = BillingService().create_invoice(
            subscription_id=int(payload["subscription_id"]),
            number=payload["number"],
            due_at=payload.get("due_at"),
        )
        db.session.commit()
    except (KeyError, TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    return (
        jsonify(
            {
                "id": value.id,
                "number": value.number,
                "amount": float(value.amount),
            }
        ),
        201,
    )


@billing_api.post("/invoices/<int:invoice_id>/payments")
@login_required
def record_payment(invoice_id):
    payload = request.get_json(silent=True) or {}
    try:
        value = BillingService().record_payment(
            invoice_id=invoice_id,
            amount=payload["amount"],
            provider=payload.get("provider", "manual"),
            provider_reference=payload.get("provider_reference"),
        )
        db.session.commit()
    except (KeyError, TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    invoice = Invoice.query.filter_by(
        id=invoice_id, organization_id=g.current_org_id
    ).first()
    return (
        jsonify(
            {
                "id": value.id,
                "invoice_id": invoice_id,
                "status": value.status,
                "invoice_status": invoice.status,
            }
        ),
        201,
    )
