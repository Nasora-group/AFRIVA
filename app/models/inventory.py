"""Inventory models for multi-store stock management."""

from decimal import Decimal

from .base import TenantAwareModel, db


class ProductCategory(TenantAwareModel):
    __tablename__ = "product_category"

    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (
        db.UniqueConstraint(
            "organization_id", "code", name="uq_product_category_org_code"
        ),
    )


class ProductStock(TenantAwareModel):
    __tablename__ = "product_stock"

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("store.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity = db.Column(db.Numeric(14, 3), nullable=False, default=Decimal("0"))
    reserved_quantity = db.Column(
        db.Numeric(14, 3), nullable=False, default=Decimal("0")
    )
    reorder_level = db.Column(
        db.Numeric(14, 3), nullable=False, default=Decimal("0")
    )

    product = db.relationship("Product")
    store = db.relationship("Store")

    __table_args__ = (
        db.UniqueConstraint(
            "organization_id",
            "product_id",
            "store_id",
            name="uq_product_stock_org_product_store",
        ),
    )


class StockMovement(TenantAwareModel):
    __tablename__ = "stock_movement"

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("store.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    movement_type = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Numeric(14, 3), nullable=False)
    reference_type = db.Column(db.String(50), nullable=True)
    reference_id = db.Column(db.Integer, nullable=True)
    note = db.Column(db.Text, nullable=True)


class ProductBatch(TenantAwareModel):
    __tablename__ = "product_batch"

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    store_id = db.Column(
        db.Integer,
        db.ForeignKey("store.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    batch_number = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.Date, nullable=True, index=True)
    quantity = db.Column(db.Numeric(14, 3), nullable=False, default=Decimal("0"))

    product = db.relationship("Product")
    store = db.relationship("Store")

    __table_args__ = (
        db.UniqueConstraint(
            "organization_id",
            "product_id",
            "store_id",
            "batch_number",
            name="uq_product_batch_org_product_store_batch",
        ),
    )
