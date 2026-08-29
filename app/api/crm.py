"""Tenant-safe CRM read endpoints used by the AFRIVA web application."""

from flask import Blueprint, g, jsonify

from app.auth import login_required
from app.models import Client, Commercial, Prospect, Prospection

crm_api = Blueprint("crm_api", __name__, url_prefix="/api/v1/crm")


def _client_json(value):
    return {"id": value.id, "name": value.name, "type": value.client_type, "city": value.city, "phone": value.phone, "status": value.status}


def _prospect_json(value):
    return {"id": value.id, "name": value.name, "contact_name": value.contact_name, "city": value.city, "phone": value.phone, "status": value.status}


@crm_api.get("/clients")
@login_required
def clients():
    rows = Client.query.filter_by(organization_id=g.current_org_id, deleted_at=None).order_by(Client.name).all()
    return jsonify({"items": [_client_json(row) for row in rows], "count": len(rows)})


@crm_api.get("/prospects")
@login_required
def prospects():
    rows = Prospect.query.filter_by(organization_id=g.current_org_id, deleted_at=None).order_by(Prospect.name).all()
    return jsonify({"items": [_prospect_json(row) for row in rows], "count": len(rows)})


@crm_api.get("/commercials")
@login_required
def commercials():
    rows = Commercial.query.filter_by(organization_id=g.current_org_id, deleted_at=None).order_by(Commercial.last_name, Commercial.first_name).all()
    return jsonify({"items": [{"id": row.id, "name": f"{row.first_name} {row.last_name}".strip(), "email": row.email, "active": row.active} for row in rows], "count": len(rows)})


@crm_api.get("/prospections")
@login_required
def prospections():
    rows = Prospection.query.filter_by(organization_id=g.current_org_id).order_by(Prospection.created_at.desc()).all()
    return jsonify({"items": [{"id": row.id, "commercial_id": row.commercial_id, "prospect_id": row.prospect_id, "status": row.status, "potential": float(row.potential or 0)} for row in rows], "count": len(rows)})
