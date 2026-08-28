"""Additional Phase 3 coverage for security-critical paths."""
import pytest
from flask import g

from app.middleware.tenant_middleware import get_current_organization, load_tenant_context
from app.repositories.base_repository import BaseRepository
from app.services.base_service import BaseService


def test_get_current_organization_requires_context(app):
    with app.test_request_context('/'):
        with pytest.raises(Exception):
            get_current_organization()


def test_repository_has_tenant_scoped_operations():
    repo = BaseRepository()
    assert hasattr(repo, "list_for_organization")
    assert hasattr(repo, "get_for_organization")
    assert hasattr(repo, "create_for_organization")


def test_service_has_current_org_operations():
    service = BaseService(None)
    assert callable(service.list_for_current_org)
    assert callable(service.get_for_current_org)
    assert callable(service.create_for_current_org)


def test_tenant_context_rejects_missing_user(app):
    with app.test_request_context('/'):
        result = load_tenant_context()
        assert result is None
        assert not hasattr(g, "current_org_id")
