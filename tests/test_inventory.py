from decimal import Decimal

from app.models import Organization, Product, ProductStock, StockMovement, Store, db
from app.services.inventory_service import InventoryService


def _setup(app, monkeypatch):
    org = Organization(name="Inventory Org", slug="inventory-org")
    db.session.add(org)
    db.session.flush()
    store = Store(organization_id=org.id, name="Dakar", code="DKR")
    product = Product(
        organization_id=org.id,
        name="Produit Stock",
        sku="STOCK-01",
        barcode="123456789",
        purchase_price=500,
        unit_price=1000,
    )
    db.session.add_all([store, product])
    db.session.commit()
    monkeypatch.setattr(
        "app.services.inventory_service.get_current_organization", lambda: org
    )
    return org, store, product


def test_inventory_purchase_then_sale_adjustment(app, monkeypatch):
    _, store, product = _setup(app, monkeypatch)
    service = InventoryService()

    stock, purchase = service.adjust_stock(product.id, store.id, "10", "purchase")
    db.session.commit()
    assert Decimal(stock.quantity) == Decimal("10")
    assert Decimal(purchase.quantity) == Decimal("10")

    stock, sale = service.adjust_stock(product.id, store.id, "3", "sale")
    db.session.commit()
    assert Decimal(stock.quantity) == Decimal("7")
    assert Decimal(sale.quantity) == Decimal("-3")
    assert StockMovement.query.count() == 2


def test_inventory_rejects_insufficient_stock(app, monkeypatch):
    _, store, product = _setup(app, monkeypatch)
    service = InventoryService()

    try:
        service.adjust_stock(product.id, store.id, "1", "sale")
    except ValueError as exc:
        assert str(exc) == "Insufficient stock"
    else:
        raise AssertionError("Expected insufficient stock error")
    db.session.rollback()
    assert ProductStock.query.count() == 0


def test_inventory_is_tenant_scoped(app, monkeypatch):
    org, store, _ = _setup(app, monkeypatch)
    other = Organization(name="Other Inventory", slug="other-inventory")
    db.session.add(other)
    db.session.flush()
    foreign_product = Product(
        organization_id=other.id, name="Foreign", sku="FOREIGN", unit_price=100
    )
    db.session.add(foreign_product)
    db.session.commit()

    service = InventoryService()
    try:
        service.adjust_stock(foreign_product.id, store.id, "1", "purchase")
    except ValueError as exc:
        assert "Product or store not found" in str(exc)
    else:
        raise AssertionError("Expected tenant isolation error")
    db.session.rollback()
    assert ProductStock.query.count() == 0
    assert org.id != other.id
