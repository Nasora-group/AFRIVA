"""Tests for the Phase 5 sales service."""

from decimal import Decimal

import pytest

from app.models import Client, Commercial, Product, Sale, SalesTarget, db
from app.services.sales import SalesValidationError, create_sale, set_sales_target


def _commercial(tenant):
    commercial = Commercial(
        organization_id=tenant.id,
        first_name="Awa",
        last_name="Diallo",
        active=True,
    )
    db.session.add(commercial)
    db.session.commit()
    return commercial


def _product(tenant, name="Product A"):
    product = Product(
        organization_id=tenant.id,
        name=name,
        unit_price=Decimal("100.00"),
        active=True,
    )
    db.session.add(product)
    db.session.commit()
    return product


def test_create_sale_calculates_totals_and_tenant_scope(app, tenant):
    commercial = _commercial(tenant)
    product = _product(tenant)

    sale = create_sale(
        organization_id=tenant.id,
        commercial_id=commercial.id,
        lines=[{"product_id": product.id, "quantity": "2"}],
    )

    assert sale.total_amount == Decimal("200.00")
    assert sale.lines[0].line_total == Decimal("200.00")
    assert Sale.query.filter_by(organization_id=tenant.id).count() == 1


def test_create_sale_rejects_cross_tenant_product(app, tenant):
    commercial = _commercial(tenant)
    other = type(tenant)(name="Other Org", slug="other-org")
    db.session.add(other)
    db.session.commit()
    product = _product(other, "Other Product")

    with pytest.raises(SalesValidationError, match="Product not found"):
        create_sale(
            organization_id=tenant.id,
            commercial_id=commercial.id,
            lines=[{"product_id": product.id, "quantity": 1}],
        )


def test_create_sale_rejects_invalid_quantity(app, tenant):
    commercial = _commercial(tenant)
    product = _product(tenant)

    with pytest.raises(SalesValidationError, match="quantity must be greater"):
        create_sale(
            organization_id=tenant.id,
            commercial_id=commercial.id,
            lines=[{"product_id": product.id, "quantity": 0}],
        )


def test_sales_target_is_upserted(app, tenant):
    commercial = _commercial(tenant)

    first = set_sales_target(
        organization_id=tenant.id,
        commercial_id=commercial.id,
        year=2026,
        month=8,
        target_amount="5000",
    )
    second = set_sales_target(
        organization_id=tenant.id,
        commercial_id=commercial.id,
        year=2026,
        month=8,
        target_amount="7500",
    )

    assert first.id == second.id
    assert second.target_amount == Decimal("7500")
    assert SalesTarget.query.filter_by(organization_id=tenant.id).count() == 1
