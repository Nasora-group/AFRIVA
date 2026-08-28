"""HTTP API for AFRIVA sales."""

from datetime import datetime
from decimal import Decimal

from flask import Blueprint, g, jsonify, request

from app.auth import login_required
from app.models import Product, Sale
from app.services.sales import SalesValidationError, create_sale, set_sales_target

sales_bp = Blueprint("sales", __name__, url_prefix="/api/sales")


def _money(value):
    return float(value or 0)


def _sale_json(sale):
    return {
        "id": sale.id,
        "organization_id": sale.organization_id,
        "commercial_id": sale.commercial_id,
        "client_id": sale.client_id,
        "sold_at": sale.sold_at.isoformat() if sale.sold_at else None,
        "status": sale.status,
        "notes": sale.notes,
        "total_amount": _money(sale.total_amount),
        "lines": [
            {
                "id": line.id,
                "product_id": line.product_id,
                "quantity": float(line.quantity),
                "unit_price": _money(line.unit_price),
                "line_total": _money(line.line_total),
            }
            for line in sale.lines
        ],
    }


@sales_bp.get("/products")
@login_required
def products():
    rows = Product.query.filter_by(organization_id=g.current_org_id, deleted_at=None, active=True).order_by(Product.name).all()
    return jsonify({"items": [{"id": p.id, "name": p.name, "sku": p.sku, "unit": p.unit, "unit_price": _money(p.unit_price)} for p in rows]})


@sales_bp.post("")
@login_required
def create():
    payload = request.get_json(silent=True) or {}
    try:
        sale = create_sale(
            organization_id=g.current_org_id,
            commercial_id=payload.get("commercial_id"),
            client_id=payload.get("client_id"),
            lines=payload.get("lines"),
            status=payload.get("status", "confirmed"),
            notes=payload.get("notes"),
        )
    except SalesValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(_sale_json(sale)), 201


@sales_bp.get("")
@login_required
def list_sales():
    query = Sale.query.filter_by(organization_id=g.current_org_id, deleted_at=None)
    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)
    commercial_id = request.args.get("commercial_id", type=int)
    if commercial_id:
        query = query.filter_by(commercial_id=commercial_id)
    rows = query.order_by(Sale.sold_at.desc(), Sale.id.desc()).all()
    return jsonify({"items": [_sale_json(sale) for sale in rows], "count": len(rows)})


@sales_bp.put("/targets")
@login_required
def target():
    payload = request.get_json(silent=True) or {}
    try:
        value = set_sales_target(
            organization_id=g.current_org_id,
            commercial_id=payload.get("commercial_id"),
            year=payload.get("year"),
            month=payload.get("month"),
            target_amount=payload.get("target_amount"),
        )
    except (SalesValidationError, TypeError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({
        "id": value.id,
        "commercial_id": value.commercial_id,
        "year": value.year,
        "month": value.month,
        "target_amount": _money(value.target_amount),
    })
