"""Shared pytest fixtures for AFRIVA CRM tests."""

import pytest
from flask import Flask, g

from app.api.pos import pos_api
from app.api.sales_dashboard import sales_dashboard_api
from app.models import (
    Organization,
    Product,
    Store,
    User,
    db,
)


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    db.init_app(app)
    app.register_blueprint(sales_dashboard_api)
    app.register_blueprint(pos_api)
    with app.app_context():
        db.create_all()
        organization = Organization(
            name="Test Organization",
            slug="test-organization",
            status="active",
        )
        db.session.add(organization)
        db.session.commit()
        app.config["TEST_ORGANIZATION_ID"] = organization.id
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def organization(app):
    with app.app_context():
        return db.session.get(Organization, app.config["TEST_ORGANIZATION_ID"])


@pytest.fixture
def user(app):
    with app.app_context():
        user = User(
            email="pos-tester@example.test",
            password_hash="test-hash",
            first_name="POS",
            last_name="Tester",
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def tenant_context(app, organization):
    with app.test_request_context():
        g.current_organization = organization
        g.current_org_id = organization.id
        yield


@pytest.fixture
def tenant_ids():
    return {"org_a": 1, "org_b": 2}


@pytest.fixture
def inventory_context(app, organization, tenant_context):
    with app.app_context():
        store = Store(
            organization_id=organization.id,
            name="Main Store",
            code="MAIN",
            active=True,
        )
        product = Product(
            organization_id=organization.id,
            name="Test Product",
            sku="TEST-001",
            unit_price=100,
            active=True,
        )
        db.session.add_all([store, product])
        db.session.commit()
        yield organization, store, product
