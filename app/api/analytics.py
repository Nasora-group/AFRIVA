"""Tenant-safe business intelligence endpoints."""

from datetime import datetime, timezone

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


def _period_start(period):
    now = datetime.now(timezone.utc)
    if period == "month":
        return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if period == "year":
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    return None


@analytics_api.get("/summary")
def summary():
    organization_id = _organization_id()
    period = request.args.get("period", "all")
    if period not in {"month", "year", "all"}:
        return jsonify({"error": "Unsupported period"}), 400

    query = db.session.query(
        func.coalesce(func.sum(Sale.total_amount), 0), func.count(Sale.id)
    ).filter(Sale.organization_id == organization_id)
    start = _period_start(period)
    if start is not None:
        query = query.filter(Sale.sold_at >= start)
    revenue, sales_count = query.one()

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
