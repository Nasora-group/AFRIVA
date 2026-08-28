"""Tenant-scoped JSON API for the AFRIVA CRM."""

from flask import Blueprint, jsonify, request

from app.models import db
from app.services.crm_service import CRMService

crm_api = Blueprint("crm_api", __name__, url_prefix="/api/v1/crm")


def _service():
    return CRMService()


def _pagination():
    return min(max(request.args.get("limit", 100, type=int), 1), 100), max(
        request.args.get("offset", 0, type=int), 0
    )


@crm_api.get("/clients")
def clients():
    limit, offset = _pagination()
    rows = _service().clients.list(limit=limit, offset=offset)
    return jsonify({"data": [{"id": r.id, "name": r.name, "phone": r.phone} for r in rows]})


@crm_api.post("/clients")
def create_client():
    payload = request.get_json(silent=True) or {}
    if not payload.get("name"):
        return jsonify({"error": "name is required"}), 400
    row = _service().create_client(
        name=payload["name"], phone=payload.get("phone"), email=payload.get("email"), address=payload.get("address")
    )
    db.session.commit()
    return jsonify({"id": row.id, "name": row.name}), 201


@crm_api.get("/prospects")
def prospects():
    limit, offset = _pagination()
    rows = _service().prospects.list(limit=limit, offset=offset)
    return jsonify({"data": [{"id": r.id, "name": r.name, "status": r.status} for r in rows]})


@crm_api.get("/contacts")
def contacts():
    limit, offset = _pagination()
    rows = _service().contacts.list(limit=limit, offset=offset)
    return jsonify({"data": [{"id": r.id, "first_name": r.first_name, "last_name": r.last_name, "phone": r.phone, "email": r.email} for r in rows]})


@crm_api.post("/contacts")
def create_contact():
    payload = request.get_json(silent=True) or {}
    if not payload.get("first_name") or not payload.get("last_name"):
        return jsonify({"error": "first_name and last_name are required"}), 400
    try:
        row = _service().create_contact(
            first_name=payload["first_name"], last_name=payload["last_name"], phone=payload.get("phone"),
            email=payload.get("email"), client_id=payload.get("client_id"), prospect_id=payload.get("prospect_id")
        )
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 404
    return jsonify({"id": row.id}), 201


@crm_api.get("/tours")
def tours():
    limit, offset = _pagination()
    rows = _service().tours.list(limit=limit, offset=offset)
    return jsonify({"data": [{"id": r.id, "name": r.name, "tour_date": r.tour_date.isoformat(), "status": r.status, "commercial_id": r.commercial_id} for r in rows]})


@crm_api.post("/tours")
def create_tour():
    payload = request.get_json(silent=True) or {}
    if not payload.get("name") or not payload.get("commercial_id"):
        return jsonify({"error": "name and commercial_id are required"}), 400
    try:
        row = _service().create_tour(commercial_id=payload["commercial_id"], name=payload["name"], status=payload.get("status", "planned"))
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 404
    return jsonify({"id": row.id}), 201


@crm_api.post("/tours/<int:tour_id>/stops")
def add_tour_stop(tour_id):
    payload = request.get_json(silent=True) or {}
    if payload.get("sequence") is None:
        return jsonify({"error": "sequence is required"}), 400
    if payload.get("client_id") is None and payload.get("prospect_id") is None:
        return jsonify({"error": "client_id or prospect_id is required"}), 400
    try:
        row = _service().add_tour_stop(
            tour_id=tour_id, sequence=payload["sequence"], status=payload.get("status", "planned"),
            planned_at=payload.get("planned_at"), latitude=payload.get("latitude"), longitude=payload.get("longitude"),
            client_id=payload.get("client_id"), prospect_id=payload.get("prospect_id")
        )
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 404
    return jsonify({"id": row.id}), 201


@crm_api.post("/visits")
def record_visit():
    payload = request.get_json(silent=True) or {}
    if not payload.get("commercial_id"):
        return jsonify({"error": "commercial_id is required"}), 400
    try:
        row = _service().record_visit(
            commercial_id=payload["commercial_id"], client_id=payload.get("client_id"), prospect_id=payload.get("prospect_id"),
            notes=payload.get("notes"), latitude=payload.get("latitude"), longitude=payload.get("longitude")
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
            commercial_id=payload["commercial_id"], prospect_id=payload.get("prospect_id"),
            outcome=payload.get("outcome", "pending"), notes=payload.get("notes")
        )
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 404
    return jsonify({"id": row.id}), 201
