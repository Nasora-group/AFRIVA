"""Tenant-scoped JSON API for the AFRIVA CRM."""

from flask import Blueprint, jsonify, request

from app.models import db
from app.services.crm_service import CRMService

crm_api = Blueprint("crm_api", __name__, url_prefix="/api/v1/crm")


def _service():
    return CRMService()


@crm_api.get("/clients")
def clients():
    limit = min(request.args.get("limit", 100, type=int), 100)
    offset = max(request.args.get("offset", 0, type=int), 0)
    rows = _service().clients.list(limit=limit, offset=offset)
    return jsonify({"data": [{"id": r.id, "name": r.name, "phone": r.phone} for r in rows]})


@crm_api.post("/clients")
def create_client():
    payload = request.get_json(silent=True) or {}
    if not payload.get("name"):
        return jsonify({"error": "name is required"}), 400
    row = _service().create_client(
        name=payload["name"],
        phone=payload.get("phone"),
        email=payload.get("email"),
        address=payload.get("address"),
    )
    db.session.commit()
    return jsonify({"id": row.id, "name": row.name}), 201


@crm_api.get("/prospects")
def prospects():
    limit = min(request.args.get("limit", 100, type=int), 100)
    offset = max(request.args.get("offset", 0, type=int), 0)
    rows = _service().prospects.list(limit=limit, offset=offset)
    return jsonify({"data": [{"id": r.id, "name": r.name, "status": r.status} for r in rows]})


@crm_api.post("/visits")
def record_visit():
    payload = request.get_json(silent=True) or {}
    if not payload.get("commercial_id"):
        return jsonify({"error": "commercial_id is required"}), 400
    try:
        row = _service().record_visit(
            commercial_id=payload["commercial_id"],
            client_id=payload.get("client_id"),
            prospect_id=payload.get("prospect_id"),
            notes=payload.get("notes"),
            latitude=payload.get("latitude"),
            longitude=payload.get("longitude"),
        )
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 404
    return jsonify({"id": row.id}), 201


@crm_api.post("/prospections")
def record_prospection():
    payload = request.get_json(silent=True) or {}
    if not payload.get("commercial_id"):
        return jsonify({"error": "commercial_id is required"}), 400
    try:
        row = _service().record_prospection(
            commercial_id=payload["commercial_id"],
            prospect_id=payload.get("prospect_id"),
            outcome=payload.get("outcome", "pending"),
            notes=payload.get("notes"),
        )
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 404
    return jsonify({"id": row.id}), 201
