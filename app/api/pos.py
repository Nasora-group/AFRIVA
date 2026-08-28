"""Tenant-scoped API for POS cash sessions."""

from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from app.services.pos_service import POSService

pos_api = Blueprint("pos_api", __name__, url_prefix="/api/v1/pos")


def _service():
    return POSService()


def _amount(payload, key):
    try:
        return Decimal(str(payload.get(key, "0.00")))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{key} must be a valid amount") from exc


@pos_api.post("/sessions/open")
def open_session():
    payload = request.get_json(silent=True) or {}
    try:
        register_id = int(payload["register_id"])
        opened_by = int(payload["opened_by"])
        opening_amount = _amount(payload, "opening_amount")
        session = _service().open_session(
            register_id, opened_by, opening_amount
        )
    except (KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({
        "id": session.id,
        "register_id": session.register_id,
        "status": session.status,
        "opening_amount": str(session.opening_amount),
    }), 201


@pos_api.post("/sessions/<int:session_id>/close")
def close_session(session_id):
    payload = request.get_json(silent=True) or {}
    try:
        closed_by = int(payload["closed_by"])
        closing_amount = _amount(payload, "closing_amount")
        session = _service().close_session(
            session_id, closed_by, closing_amount
        )
    except (KeyError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({
        "id": session.id,
        "status": session.status,
        "closing_amount": str(session.closing_amount),
    })
