"""Behavioral coverage for Phase 3 security-critical paths."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from flask import g, session
from werkzeug.security import generate_password_hash

from app import create_app
from app.auth import authenticate, load_current_user, login_required, login_user, logout_user
from app.config import Config
from app.middleware import tenant_middleware
from app.middleware.tenant_middleware import get_current_organization, get_current_org_id, load_tenant_context
from app.models import db, OrganizationUser, User
from app.repositories.base_repository import BaseRepository
from app.services import base_service
from app.services.base_service import BaseService


@pytest.fixture
def app():
    class TestConfig(Config):
        TESTING = True
        SECRET_KEY = "coverage-only-secret"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        SESSION_COOKIE_SECURE = False

    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


def test_authenticate_success_and_failures(app):
    user = User(email="coverage@example.test", password_hash=generate_password_hash("secret"), status="active")
    db.session.add(user)
    db.session.commit()
    with app.test_request_context("/"):
        assert authenticate(user.email, "secret").id == user.id
        assert authenticate(user.email, "wrong") is None
        assert authenticate("missing@example.test", "secret") is None


def test_auth_session_lifecycle(app):
    user = User(email="session@example.test", password_hash=generate_password_hash("secret"), status="active")
    db.session.add(user)
    db.session.commit()
    with app.test_request_context("/"):
        login_user(user)
        assert session["user_id"] == user.id
        assert g.current_user.id == user.id
        assert load_current_user().id == user.id
        logout_user()
        assert "user_id" not in session
        assert not hasattr(g, "current_user")


def test_load_current_user_invalid_or_inactive_session(app):
    inactive = User(email="inactive@example.test", password_hash=generate_password_hash("secret"), status="suspended")
    db.session.add(inactive)
    db.session.commit()
    with app.test_request_context("/"):
        session["user_id"] = 999999
        assert load_current_user() is None
        assert "user_id" not in session
        session["user_id"] = inactive.id
        assert load_current_user() is None
        assert "user_id" not in session


def test_login_required_allows_authenticated_user(app):
    calls = []

    @login_required
    def protected(value):
        calls.append(value)
        return "ok"

    user = User(email="protected@example.test", password_hash=generate_password_hash("secret"), status="active")
    db.session.add(user)
    db.session.commit()
    with app.test_request_context("/"):
        session["user_id"] = user.id
        assert protected("allowed") == "ok"
        assert calls == ["allowed"]


def test_login_required_rejects_anonymous(app):
    @login_required
    def protected():
        return "never"

    with app.test_request_context("/"):
        with pytest.raises(Exception) as exc:
            protected()
        assert getattr(exc.value, "code", None) == 401


def test_tenant_context_missing_user_is_safe(app):
    with app.test_request_context("/"):
        assert load_tenant_context() is None
        assert not hasattr(g, "current_org_id")


def test_tenant_context_selects_membership_and_sets_context(app, monkeypatch):
    user = SimpleNamespace(id=10)
    membership = SimpleNamespace(user_id=10, organization_id=20, status="active")
    organization = SimpleNamespace(id=20, status="active")
    query = Mock()
    query.filter_by.return_value = query
    query.order_by.return_value = query
    query.first.return_value = membership
    monkeypatch.setattr(tenant_middleware.OrganizationUser, "query", query)
    monkeypatch.setattr(tenant_middleware, "db_get_organization", lambda org_id: organization)
    with app.test_request_context("/"):
        g.current_user = user
        session["current_org_id"] = 20
        load_tenant_context()
        assert g.current_membership is membership
        assert g.current_organization is organization
        assert g.current_org_id == 20


def test_tenant_context_falls_back_to_first_membership(app, monkeypatch):
    user = SimpleNamespace(id=10)
    membership = SimpleNamespace(user_id=10, organization_id=30, status="active")
    organization = SimpleNamespace(id=30, status="active")
    query = Mock()
    query.filter_by.return_value = query
    query.order_by.return_value = query
    query.first.side_effect = [None, membership]
    monkeypatch.setattr(tenant_middleware.OrganizationUser, "query", query)
    monkeypatch.setattr(tenant_middleware, "db_get_organization", lambda org_id: organization)
    with app.test_request_context("/"):
        g.current_user = user
        load_tenant_context()
        assert get_current_org_id() == 30


def test_tenant_context_rejects_no_membership(app, monkeypatch):
    query = Mock()
    query.filter_by.return_value = query
    query.order_by.return_value = query
    query.first.return_value = None
    monkeypatch.setattr(tenant_middleware.OrganizationUser, "query", query)
    with app.test_request_context("/"):
        g.current_user = SimpleNamespace(id=10)
        with pytest.raises(Exception) as exc:
            load_tenant_context()
        assert getattr(exc.value, "code", None) == 403


def test_tenant_context_rejects_suspended_organization(app, monkeypatch):
    membership = SimpleNamespace(user_id=10, organization_id=40, status="active")
    organization = SimpleNamespace(id=40, status="suspended")
    query = Mock()
    query.filter_by.return_value = query
    query.first.return_value = membership
    monkeypatch.setattr(tenant_middleware.OrganizationUser, "query", query)
    monkeypatch.setattr(tenant_middleware, "db_get_organization", lambda org_id: organization)
    with app.test_request_context("/"):
        g.current_user = SimpleNamespace(id=10)
        with pytest.raises(Exception) as exc:
            load_tenant_context()
        assert getattr(exc.value, "code", None) == 403


def test_get_current_organization_and_id_require_context(app):
    with app.test_request_context("/"):
        with pytest.raises(Exception) as exc:
            get_current_organization()
        assert getattr(exc.value, "code", None) == 403
        with pytest.raises(Exception) as exc:
            get_current_org_id()
        assert getattr(exc.value, "code", None) == 403


def test_repository_filters_and_soft_deletes(app, monkeypatch):
    repo = BaseRepository()
    query = Mock()
    query.filter.return_value = query
    entity = SimpleNamespace(organization_id=1, id=2, deleted_at=None, name="one")
    query.all.return_value = [entity]
    query.first.return_value = entity

    class FakeColumn:
        def __eq__(self, other):
            return ("eq", other)

        def is_(self, value):
            return ("is", value)

    class FakeModel:
        organization_id = FakeColumn()
        id = FakeColumn()
        deleted_at = FakeColumn()

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    FakeModel.query = query
    repo.model = FakeModel
    monkeypatch.setattr(db.session, "add", Mock())
    monkeypatch.setattr(db.session, "flush", Mock())
    assert repo.get_for_organization(1, 2) is entity
    assert repo.list_for_organization(1, status="active", organization_id=999) == [entity]
    created = repo.create_for_organization(1, organization_id=999, name="X")
    assert created.organization_id == 1
    assert created.name == "X"
    deleted = repo.soft_delete_for_organization(1, 2)
    assert deleted is entity
    assert entity.deleted_at is not None


def test_repository_soft_delete_missing_entity(app, monkeypatch):
    repo = BaseRepository()
    monkeypatch.setattr(repo, "get_for_organization", lambda org_id, entity_id: None)
    assert repo.soft_delete_for_organization(1, 99) is None


def test_service_delegates_all_tenant_operations(monkeypatch):
    repository = Mock()
    service = BaseService(repository)
    monkeypatch.setattr(base_service, "get_current_org_id", lambda: 77)
    repository.list_for_organization.return_value = ["a"]
    repository.get_for_organization.return_value = "b"
    repository.create_for_organization.return_value = "c"
    repository.soft_delete_for_organization.return_value = "d"
    assert service.list_for_current_org(status="active") == ["a"]
    assert service.get_for_current_org(2) == "b"
    assert service.create_for_current_org(name="x") == "c"
    assert service.soft_delete_for_current_org(3) == "d"


def test_service_without_tenant_context_propagates_forbidden(monkeypatch):
    service = BaseService(Mock())
    monkeypatch.setattr(base_service, "get_current_org_id", Mock(side_effect=Exception("403")))
    with pytest.raises(Exception):
        service.list_for_current_org()
