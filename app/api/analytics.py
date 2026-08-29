"""Tenant-safe business intelligence endpoints."""

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.middleware.tenant_middleware import get_current_organization
from app.models import Client, Prospection, Sale, db

analytics_api = Blueprint("analytics_api", __name__, url_prefix="/api/v1/analytics")


def _organization_id():
    organization = get_current_organization()
    if organization is None:
        raise ValueError("No current organization")
    return organization.id


@analytics_api.get("/summary")
def summary():
    organization_id = _organization_id()
    period = request.args.get("period", "all")
    if period not in {"month", "year", "all"}:
        return jsonify({"error": "Unsupported period"}), 400

    revenue, sales_count = db.session.query(
        func.coalesce(func.sum(Sale.total_amount), 0), func.count(Sale.id)
    ).filter(Sale.organization_id == organization_id).one()

    return jsonify(
        {
            "period": period,
            "revenue": str(revenue),
            "sales_count": sales_count,
            "clients": Client.query.filter_by(
                organization_id=organization_id
            ).count(),
            "prospections": Prospection.query.filter_by(
                organization_id=organization_id
            ).count(),
        }
    )
