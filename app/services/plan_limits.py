"""Server-side SaaS plan limit enforcement for AFRIVA.

All checks are organization-scoped and fail closed when no active subscription
is available.  Route/service layers can call these helpers before creating
users, stores, or products.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import func

from app.extensions import db
from app.models.billing import Subscription


@dataclass(frozen=True)
class PlanLimitError(Exception):
    resource: str
    limit: int
    current: int

    def __str__(self) -> str:
        return (
            f"Plan limit reached for {self.resource}: "
            f"{self.current}/{self.limit}"
        )


def active_subscription(organization_id: int) -> Subscription | None:
    """Return the current active/trial subscription for an organization."""
    return (
        Subscription.query.filter(
            Subscription.organization_id == organization_id,
            Subscription.status.in_(["trialing", "active"]),
        )
        .order_by(Subscription.current_period_end.desc())
        .first()
    )


def enforce_limit(
    organization_id: int,
    resource: str,
    current_count: int,
) -> None:
    """Raise when creating one more resource would exceed the plan limit."""
    subscription = active_subscription(organization_id)
    if subscription is None or subscription.plan is None:
        raise PlanLimitError(resource, 0, current_count)

    limit = getattr(subscription.plan, f"max_{resource}", None)
    if limit is None:
        raise ValueError(f"Unknown plan resource: {resource}")

    # A non-positive limit means the resource is unavailable on the plan.
    if current_count >= limit:
        raise PlanLimitError(resource, limit, current_count)


def count_rows(model: Any, organization_id: int) -> int:
    """Count tenant rows without loading them into memory."""
    if not hasattr(model, "organization_id"):
        raise ValueError(f"{model.__name__} is not organization-scoped")
    return int(
        db.session.query(func.count(model.id))
        .filter(model.organization_id == organization_id)
        .scalar()
        or 0
    )


def check_user_limit(organization_id: int, user_model: Any) -> None:
    enforce_limit(organization_id, "users", count_rows(user_model, organization_id))


def check_store_limit(organization_id: int, store_model: Any) -> None:
    enforce_limit(organization_id, "stores", count_rows(store_model, organization_id))


def check_product_limit(organization_id: int, product_model: Any) -> None:
    enforce_limit(
        organization_id, "products", count_rows(product_model, organization_id)
    )
