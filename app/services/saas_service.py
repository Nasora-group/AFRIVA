"""SaaS plan, subscription and tenant quota enforcement."""

from app.middleware.tenant_middleware import get_current_org_id
from app.models import OrganizationUser, Product, Store, Subscription
from app.models.base import utcnow


class QuotaExceeded(ValueError):
    """Raised when a tenant reaches a plan quota."""


class SaaSService:
    """Central server-side enforcement for tenant SaaS limits."""

    def organization_id(self):
        return get_current_org_id()

    def subscription(self):
        organization_id = self.organization_id()
        return (
            Subscription.query.filter(
                Subscription.organization_id == organization_id,
                Subscription.status.in_(("active", "trialing")),
                Subscription.current_period_end > utcnow(),
            )
            .order_by(Subscription.id.desc())
            .first()
        )

    def plan(self):
        subscription = self.subscription()
        if subscription is None:
            raise ValueError("Active subscription required")
        return subscription.plan

    def usage(self):
        organization_id = self.organization_id()
        return {
            "users": OrganizationUser.query.filter_by(
                organization_id=organization_id, status="active"
            ).count(),
            "stores": Store.query.filter_by(
                organization_id=organization_id, active=True
            ).count(),
            "products": Product.query.filter_by(
                organization_id=organization_id, active=True
            ).count(),
        }

    def limits(self):
        plan = self.plan()
        return {
            "users": plan.max_users,
            "stores": plan.max_stores,
            "products": plan.max_products,
        }

    def assert_can_create(self, resource, additional=1):
        if resource not in {"users", "stores", "products"}:
            raise ValueError("Unsupported quota resource")
        usage = self.usage()[resource]
        limit = self.limits()[resource]
        if limit is not None and usage + additional > limit:
            raise QuotaExceeded(
                f"Quota {resource} atteinte pour le plan actuel ({limit})."
            )
        return True

    def snapshot(self):
        subscription = self.subscription()
        plan = subscription.plan if subscription else None
        usage = self.usage()
        limits = {
            "users": plan.max_users if plan else None,
            "stores": plan.max_stores if plan else None,
            "products": plan.max_products if plan else None,
        }
        return {
            "subscription": {
                "status": subscription.status,
                "plan": plan.code,
                "plan_name": plan.name,
                "current_period_end": subscription.current_period_end.isoformat(),
            }
            if subscription and plan
            else None,
            "usage": usage,
            "limits": limits,
        }
