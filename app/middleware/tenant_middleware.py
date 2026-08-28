"""Server-side tenant context. Never trust organization_id from request input."""

from flask import abort, g, session

from app.models.organization import Organization
from app.models.user import OrganizationUser


def load_tenant_context():
    user = getattr(g, "current_user", None)
    if user is None:
        return

    org_id = session.get("current_org_id")
    membership = None

    if org_id is not None:
        membership = OrganizationUser.query.filter_by(
            user_id=user.id, organization_id=org_id, status="active"
        ).first()

    if membership is None:
        membership = (
            OrganizationUser.query.filter_by(user_id=user.id, status="active")
            .order_by(OrganizationUser.id.asc())
            .first()
        )

    if membership is None:
        abort(403)

    organization = db_get_organization(membership.organization_id)
    if organization is None or organization.status in {"suspended", "deleted"}:
        abort(403)

    session["current_org_id"] = organization.id
    g.current_membership = membership
    g.current_organization = organization
    g.current_org_id = organization.id


def db_get_organization(org_id):
    return Organization.query.filter_by(id=org_id).first()


def get_current_organization():
    organization = getattr(g, "current_organization", None)
    if organization is None:
        abort(403)
    return organization


def get_current_org_id():
    return get_current_organization().id
