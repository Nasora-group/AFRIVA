"""REST API for stores, registers, cash sessions and POS sales."""

from flask import Blueprint, g, jsonify, request

from app.auth import login_required
from app.models import CashSession, POSRegister, Store
from app.services.pos_service import (
    POSValidationError,
    close_session,
    create_pos_sale,
    open_session,
)

pos_bp = Blueprint("pos", __name__, url_prefix="/api/pos")


@pos_bp.get("/stores")
@login_required
def stores():
    rows = (
        Store.query.filter_by(
            organization_id=g.current_org_id,
            deleted_at=None,
            active=True,
        )
        .order_by(Store.name)
        .all()
    )
    return jsonify(
        {
            "items": [
                {"id": s.id, "name": s.name, "code": s.code}
                for s in rows
            ]
        }
    )


@pos_bp.get("/registers")
@login_required
def registers():
    rows = (
        POSRegister.query.filter_by(
            organization_id=g.current_org_id,
            deleted_at=None,
            active=True,
        )
        .order_by(POSRegister.name)
        .all()
    )
    return jsonify(
        {
            "items": [
                {
                    "id": r.id,
                    "store_id": r.store_id,
                    "name": r.name,
                    "code": r.code,
                }
                for r in rows
            ]
        }
    )


@pos_bp.post("/sessions")
@login_required
def open_cash_session():
    payload = request.get_json(silent=True) or {}
    try:
        value = open_session(
            organization_id=g.current_org_id,
            register_id=payload.get("register_id"),
            user_id=g.current_user.id,
            opening_cash=payload.get("opening_cash", 0),
        )
    except POSValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(
        {
            "id": value.id,
            "register_id": value.register_id,
            "status": value.status,
            "opening_cash": float(value.opening_cash),
        }
    ), 201


@pos_bp.post("/sessions/<int:session_id>/close")
@login_required
def close_cash_session(session_id):
    payload = request.get_json(silent=True) or {}
    try:
        value = close_session(
            organization_id=g.current_org_id,
            session_id=session_id,
            user_id=g.current_user.id,
            closing_cash=payload.get("closing_cash", 0),
        )
    except POSValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(
        {
            "id": value.id,
            "status": value.status,
            "closing_cash": float(value.closing_cash),
        }
    )


@pos_bp.post("/sales")
@login_required
def create_sale():
    payload = request.get_json(silent=True) or {}
    try:
        sale = create_pos_sale(
            organization_id=g.current_org_id,
            session_id=payload.get("session_id"),
            lines=payload.get("lines"),
            payments=payload.get("payments"),
        )
    except (POSValidationError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(
        {
            "id": sale.id,
            "reference": sale.reference,
            "status": sale.status,
            "total_amount": float(sale.total_amount),
            "payments": [
                {"method": p.method, "amount": float(p.amount)} for p in sale.payments
            ],
        }
    ), 201


@pos_bp.get("/sessions")
@login_required
def sessions():
    rows = (
        CashSession.query.filter_by(organization_id=g.current_org_id)
        .order_by(CashSession.opened_at.desc())
        .all()
    )
    return jsonify(
        {
            "items": [
                {
                    "id": s.id,
                    "register_id": s.register_id,
                    "status": s.status,
                    "opening_cash": float(s.opening_cash),
                    "closing_cash": float(s.closing_cash or 0),
                }
                for s in rows
            ]
        }
    )
