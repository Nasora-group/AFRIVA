"""Tenant-safe business intelligence endpoints."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.middleware.tenant_middleware import get_current_organization
from app.models import Client, POSSale, Prospection, Sale, db

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

    start = _period_start(period)

    sales_query = db.session.query(
        func.coalesce(func.sum(Sale.total_amount), 0), func.count(Sale.id)
    ).filter(Sale.organization_id == organization_id)
    pos_query = db.session.query(
        func.coalesce(func.sum(POSSale.total_amount), 0), func.count(POSSale.id)
    ).filter(
        POSSale.organization_id == organization_id,
        POSSale.status == "confirmed",
    )
    if start is not None:
        sales_query = sales_query.filter(Sale.sold_at >= start)
        pos_query = pos_query.filter(POSSale.sold_at >= start)

    sales_revenue, sales_count = sales_query.one()
    pos_revenue, pos_count = pos_query.one()
    revenue = sales_revenue + pos_revenue
    total_sales = sales_count + pos_count

    return jsonify(
        {
            "period": period,
            "revenue": str(revenue),
            "sales_count": total_sales,
            "clients": Client.query.filter_by(
                organization_id=organization_id
            ).count(),
            "prospections": Prospection.query.filter_by(
                organization_id=organization_id
            ).count(),
        }
    )
