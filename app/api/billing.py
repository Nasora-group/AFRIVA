"""Tenant-aware SaaS billing endpoints."""

from flask import Blueprint, g, jsonify, request

from app.auth import login_required
from app.models import Invoice, Plan, Subscription, db
from app.services.billing_service import BillingService
from app.services.saas_service import SaaSService

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


def _subscription_json(value):
    if value is None:
        return None
    return {
        "id": value.id,
        "plan": value.plan.code,
        "plan_name": value.plan.name,
        "status": value.status,
        "billing_interval": value.billing_interval,
        "trial_ends_at": value.trial_ends_at.isoformat()
        if value.trial_ends_at
        else None,
        "current_period_start": value.current_period_start.isoformat(),
        "current_period_end": value.current_period_end.isoformat(),
    }


@billing_api.get("/plans")
def plans():
    rows = Plan.query.filter_by(active=True).order_by(Plan.monthly_price, Plan.id).all()
    return jsonify({"items": [_plan_json(plan) for plan in rows]})


@billing_api.get("/subscription")
@login_required
def subscription():
    service = BillingService()
    value = (
        Subscription.query.filter_by(
            organization_id=g.current_org_id, status="active"
        ).first()
        or Subscription.query.filter_by(
            organization_id=g.current_org_id, status="trialing"
        ).first()
    )
    if value is not None:
        value = service.refresh_subscription_status(value)
        db.session.commit()
    if value is not None and value.status == "expired":
        value = None
    return jsonify({"subscription": _subscription_json(value)})


@billing_api.get("/usage")
@login_required
def usage():
    """Return tenant-scoped quota usage and limits."""
    return jsonify(SaaSService().snapshot())


@billing_api.get("/invoices")
@login_required
def invoices():
    rows = (
        Invoice.query.filter_by(organization_id=g.current_org_id)
        .order_by(Invoice.issued_at.desc(), Invoice.id.desc())
        .limit(100)
        .all()
    )
    return jsonify(
        {
            "items": [
                {
                    "id": row.id,
                    "number": row.number,
                    "status": row.status,
                    "amount": float(row.amount),
                    "currency": row.currency,
                    "issued_at": row.issued_at.isoformat(),
                    "due_at": row.due_at.isoformat() if row.due_at else None,
                    "paid_at": row.paid_at.isoformat() if row.paid_at else None,
                }
                for row in rows
            ]
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


@billing_api.patch("/subscriptions")
@login_required
def change_subscription():
    payload = request.get_json(silent=True) or {}
    try:
        value = BillingService().change_plan(
            plan_code=payload["plan_code"],
            interval=payload.get("interval", "monthly"),
            trial=bool(payload.get("trial", False)),
        )
        db.session.commit()
    except (KeyError, TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    return jsonify({"subscription": _subscription_json(value)}), 200


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
