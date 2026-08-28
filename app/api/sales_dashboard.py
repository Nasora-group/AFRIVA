"""Sales dashboard metrics API."""

from datetime import date

from flask import Blueprint, jsonify, request

from app.services.sales_dashboard_service import SalesDashboardService

sales_dashboard_api = Blueprint(
    "sales_dashboard_api", __name__, url_prefix="/api/v1/sales/dashboard"
)


def _date(value, default):
    if not value:
        return default
    return date.fromisoformat(value)


@sales_dashboard_api.get("")
def dashboard():
    try:
        start = _date(request.args.get("start"), date.today().replace(day=1))
        end = _date(request.args.get("end"), date.today())
        if start > end:
            return jsonify({"error": "start must be before or equal to end"}), 400
        metrics = SalesDashboardService().summary(
            start, end, request.args.get("commercial_id", type=int)
        )
        return jsonify(
            {
                "revenue": str(metrics["revenue"]),
                "target": str(metrics["target"]),
                "attainment_rate": str(metrics["attainment_rate"]),
                "sales_count": metrics["sales_count"],
                "daily_revenue": {
                    key: str(value) for key, value in metrics["daily_revenue"].items()
                },
                "revenue_by_commercial": {
                    str(key): str(value)
                    for key, value in metrics["revenue_by_commercial"].items()
                },
            }
        )
    except ValueError:
        return jsonify({"error": "dates must use YYYY-MM-DD format"}), 400
