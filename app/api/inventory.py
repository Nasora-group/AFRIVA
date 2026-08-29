"""Inventory API endpoints for Phase 7."""

from flask import Blueprint, jsonify, request

from app.auth import login_required
from app.models import db
from app.services.inventory_service import InventoryService

inventory_api = Blueprint("inventory_api", __name__, url_prefix="/api/v1/inventory")


@inventory_api.post("/movements")
@login_required
def create_movement():
    payload = request.get_json(silent=True) or {}
    try:
        stock, movement = InventoryService().adjust_stock(
            product_id=int(payload["product_id"]),
            store_id=int(payload["store_id"]),
            quantity=payload["quantity"],
            movement_type=payload.get("movement_type", "adjustment"),
            reference_type=payload.get("reference_type"),
            reference_id=payload.get("reference_id"),
            note=payload.get("note"),
        )
        db.session.commit()
    except (KeyError, TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400

    return jsonify(
        {
            "stock_id": stock.id,
            "product_id": stock.product_id,
            "store_id": stock.store_id,
            "quantity": str(stock.quantity),
            "movement_id": movement.id,
            "movement_type": movement.movement_type,
            "delta": str(movement.quantity),
        }
    ), 201
