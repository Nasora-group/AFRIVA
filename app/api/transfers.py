"""API endpoints for stock transfers."""

from flask import Blueprint, jsonify, request

from app.auth import login_required
from app.models import db
from app.services.inventory_service import InventoryService

transfers_api = Blueprint("transfers_api", __name__, url_prefix="/api/v1/inventory")


@transfers_api.post("/transfers")
@login_required
def create_transfer():
    payload = request.get_json(silent=True) or {}
    try:
        transfer = InventoryService().create_transfer(
            int(payload["source_store_id"]),
            int(payload["destination_store_id"]),
            payload["items"],
            payload.get("reference"),
            payload.get("note"),
        )
        db.session.commit()
        return jsonify({"id": transfer.id, "status": transfer.status}), 201
    except (KeyError, TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400


@transfers_api.post("/transfers/<int:transfer_id>/complete")
@login_required
def complete_transfer(transfer_id):
    try:
        transfer = InventoryService().complete_transfer(transfer_id)
        db.session.commit()
        return jsonify({"id": transfer.id, "status": transfer.status}), 200
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
