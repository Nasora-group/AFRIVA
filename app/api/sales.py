"""Tenant-scoped JSON API for sales."""

from datetime import date

from flask import Blueprint, jsonify, request

from app.models import db
from app.services.sales_service import SalesService

sales_api = Blueprint("sales_api", __name__, url_prefix="/api/v1/sales")


def _service():
    return SalesService()


def _pagination():
    return min(max(request.args.get("limit", 100, type=int), 1), 100), max(
        request.args.get("offset", 0, type=int), 0
    )


def _sale_date(value):
    if value in (None, ""):
        return date.today()
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("sale_date must use YYYY-MM-DD format") from exc


@sales_api.get("/products")
def products():
    limit, offset = _pagination()
    rows = _service().products.list(limit=limit, offset=offset)
    data = [
        {
            "id": r.id,
            "name": r.name,
            "sku": r.sku,
            "unit_price": str(r.unit_price),
            "active": r.active,
        }
        for r in rows
    ]
    return jsonify({"data": data})


@sales_api.post("/products")
def create_product():
    payload = request.get_json(silent=True) or {}
    if not payload.get("name"):
        return jsonify({"error": "name is required"}), 400
    try:
        price = float(payload.get("unit_price", 0))
        if price < 0:
            raise ValueError
        row = _service().create_product(
            name=payload["name"],
            sku=payload.get("sku"),
            unit_price=price,
            active=payload.get("active", True),
        )
        db.session.commit()
    except ValueError:
        db.session.rollback()
        return jsonify({"error": "unit_price must be non-negative"}), 400
    return jsonify({"id": row.id, "name": row.name}), 201


@sales_api.post("/sales")
def create_sale():
    payload = request.get_json(silent=True) or {}
    try:
        row = _service().create_sale(
            items=payload.get("items", []),
            commercial_id=payload.get("commercial_id"),
            client_id=payload.get("client_id"),
            sale_date=_sale_date(payload.get("sale_date")),
            status=payload.get("status", "confirmed"),
        )
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    return jsonify({"id": row.id, "total_amount": str(row.total_amount)}), 201


@sales_api.get("/sales")
def sales():
    limit, offset = _pagination()
    rows = _service().sales.list(limit=limit, offset=offset)
    data = [
        {
            "id": r.id,
            "sale_date": r.sale_date.isoformat(),
            "status": r.status,
            "total_amount": str(r.total_amount),
            "commercial_id": r.commercial_id,
            "client_id": r.client_id,
        }
        for r in rows
    ]
    return jsonify({"data": data})


@sales_api.post("/targets")
def create_target():
    payload = request.get_json(silent=True) or {}
    try:
        row = _service().set_target(
            year=int(payload["year"]),
            month=int(payload["month"]),
            target_amount=payload["target_amount"],
            commercial_id=payload.get("commercial_id"),
        )
        db.session.commit()
    except (KeyError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc) or "invalid target"}), 400
    return jsonify({"id": row.id}), 201


@sales_api.get("/targets")
def targets():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    if year is None or month is None:
        return jsonify({"error": "year and month are required"}), 400
    rows = _service().targets.for_period(
        year, month, request.args.get("commercial_id", type=int)
    )
    data = [
        {
            "id": r.id,
            "year": r.year,
            "month": r.month,
            "target_amount": str(r.target_amount),
            "commercial_id": r.commercial_id,
        }
        for r in rows
    ]
    return jsonify({"data": data})
