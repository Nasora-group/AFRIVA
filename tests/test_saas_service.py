from datetime import timedelta

import pytest

from app.models import OrganizationUser, Product, Store, Subscription
from app.models.base import utcnow
from app.services.saas_service import QuotaExceeded, SaaSService


def test_saas_usage_limits_and_quota(app, organization, user, plan, db):
    subscription = Subscription(
        organization_id=organization.id,
        plan_id=plan.id,
        status="active",
        current_period_end=utcnow() + timedelta(days=30),
    )
    db.session.add(subscription)
    db.session.add(
        OrganizationUser(
            user_id=user.id,
            organization_id=organization.id,
            role_id=1,
            status="active",
        )
    )
    db.session.add(Store(organization_id=organization.id, name="Store 1", active=True))
    db.session.add(Product(organization_id=organization.id, name="Product 1", active=True))
    db.session.commit()

    service = SaaSService()
    assert service.plan().id == plan.id
    assert service.usage()["users"] >= 1
    assert service.limits()["users"] == plan.max_users
    assert service.assert_can_create("products") is True
    assert service.snapshot()["subscription"]["status"] == "active"


def test_saas_requires_active_subscription(app, organization, user):
    with app.test_request_context("/"):
        from flask import g
        from flask import session
        g.current_organization = organization
        g.current_org_id = organization.id
        session["current_org_id"] = organization.id
        service = SaaSService()
        with pytest.raises(ValueError, match="Active subscription"):
            service.plan()


def test_saas_rejects_unsupported_resource(app, organization):
    with app.test_request_context("/"):
        from flask import g
        g.current_organization = organization
        g.current_org_id = organization.id
        service = SaaSService()
        with pytest.raises(ValueError, match="Unsupported quota resource"):
            service.assert_can_create("orders")
