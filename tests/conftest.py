"""Pytest configuration for AFRIVA Phase 3.

Database-backed fixtures will be enabled once the Flask/SQLAlchemy runtime
configuration is added. No production database is touched by these tests.
"""
import pytest


@pytest.fixture
def tenant_ids():
    return {"org_a": 1, "org_b": 2}
