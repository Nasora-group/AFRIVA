"""Pytest configuration for isolated AFRIVA service tests."""

import pytest
from flask import g

from app import create_app
from app.models import db
from app.models.organization import Organization


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def tenant(app):
    organization = Organization(name="Test Org", slug="test-org")
    db.session.add(organization)
    db.session.commit()
    g.current_organization = organization
    return organization


@pytest.fixture
def tenant_ids():
    return {"org_a": 1, "org_b": 2}
