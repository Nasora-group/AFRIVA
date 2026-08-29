"""Pytest configuration for isolated AFRIVA service tests."""

from decimal import Decimal

import pytest
from flask import g

from app import create_app
from app.models import Product, Store, db
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
def inventory_context(app):
    organization = Organization(name="Inventory Test Org", slug="inventory-test-org")
    db.session.add(organization)
    db.session.flush()
    source = Store(
        organization_id=organization.id,
        name="Main Store",
        code="MAIN",
    )
    destination = Store(
        organization_id=organization.id,
        name="Secondary Store",
        code="SECONDARY",
    )
    product = Product(
        organization_id=organization.id,
        name="Test Product",
        sku="TEST-001",
        purchase_price=Decimal("5.00"),
        unit_price=Decimal("10.00"),
    )
    db.session.add_all([source, destination, product])
    db.session.commit()
    g.current_organization = organization
    return organization, source, destination, product
