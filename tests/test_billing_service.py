"""Unit tests for SaaS billing rules that do not require a production database."""

from datetime import datetime, timezone

import pytest

from app.services.billing_service import BillingService


def test_period_end_monthly():
    start = datetime(2026, 8, 28, tzinfo=timezone.utc)
    assert BillingService._period_end(start, "monthly") == datetime(
        2026, 9, 27, tzinfo=timezone.utc
    )


def test_period_end_yearly():
    start = datetime(2026, 8, 28, tzinfo=timezone.utc)
    assert BillingService._period_end(start, "yearly") == datetime(
        2027, 8, 28, tzinfo=timezone.utc
    )


def test_period_end_rejects_unknown_interval():
    with pytest.raises(ValueError, match="Unsupported billing interval"):
        BillingService._period_end(datetime.now(timezone.utc), "weekly")
