"""Inventory models for multi-store stock management."""

from decimal import Decimal

from .base import TenantAwareModel, db


class ProductCategory(TenantAwareModel):
    __tablename__ = "product_category"

    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)


class ProductStock(TenantAwareModel):
    __tablename__ = "product_stock"

    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    store_id = db.Column(
        db.Integer, db.ForeignKey("store.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity = db.Column(db.Numeric(14, 3), nullable=False, default=Decimal("0"))
    reserved_quantity = db.Column(db.Numeric(14, 3), nullable=False, default=Decimal("0"))
    reorder_level = db.Column(db.Numeric(14, 3), nullable=False, default=Decimal("0"))

    product = db.relationship("Product")
    store = db.relationship("Store")


class StockMovement(TenantAwareModel):
    __tablename__ = "stock_movement"

    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    store_id = db.Column(
        db.Integer, db.ForeignKey("store.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    movement_type = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Numeric(14, 3), nullable=False)
    reference_type = db.Column(db.String(50), nullable=True)
    reference_id = db.Column(db.Integer, nullable=True)
    note = db.Column(db.Text, nullable=True)


class ProductBatch(TenantAwareModel):
    __tablename__ = "product_batch"

    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    store_id = db.Column(
        db.Integer, db.ForeignKey("store.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    batch_number = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.Date, nullable=True, index=True)
    quantity = db.Column(db.Numeric(14, 3), nullable=False, default=Decimal("0"))

    product = db.relationship("Product")
    store = db.relationship("Store")


class StockTransfer(TenantAwareModel):
    __tablename__ = "stock_transfer"

    source_store_id = db.Column(
        db.Integer,
        db.ForeignKey("store.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    destination_store_id = db.Column(
        db.Integer,
        db.ForeignKey("store.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status = db.Column(db.String(30), nullable=False, default="draft", index=True)
    reference = db.Column(db.String(100), nullable=True, index=True)
    note = db.Column(db.Text, nullable=True)

    source_store = db.relationship("Store", foreign_keys=[source_store_id])
    destination_store = db.relationship("Store", foreign_keys=[destination_store_id])
    items = db.relationship(
        "StockTransferItem", back_populates="transfer", cascade="all, delete-orphan"
    )


class StockTransferItem(TenantAwareModel):
    __tablename__ = "stock_transfer_item"

    transfer_id = db.Column(
        db.Integer,
        db.ForeignKey("stock_transfer.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity = db.Column(db.Numeric(14, 3), nullable=False)
    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("product_batch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    transfer = db.relationship("StockTransfer", back_populates="items")
    product = db.relationship("Product")
    batch = db.relationship("ProductBatch")
