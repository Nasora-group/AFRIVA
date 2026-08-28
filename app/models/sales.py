"""Sales domain models for AFRIVA."""

from datetime import date
from decimal import Decimal

from .base import TenantAwareModel, db


class Product(TenantAwareModel):
    __tablename__ = "product"

    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), nullable=True, index=True)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    active = db.Column(db.Boolean, nullable=False, default=True)


class Sale(TenantAwareModel):
    __tablename__ = "sale"

    sale_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    status = db.Column(db.String(50), nullable=False, default="confirmed")
    commercial_id = db.Column(db.Integer, db.ForeignKey("commercial.id"), nullable=True, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=True, index=True)
    cash_session_id = db.Column(
        db.Integer, db.ForeignKey("cash_session.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))

    items = db.relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = db.relationship("Payment", back_populates="sale", cascade="all, delete-orphan")
    cash_session = db.relationship("CashSession", back_populates="sales")


class SaleItem(TenantAwareModel):
    __tablename__ = "sale_item"

    sale_id = db.Column(db.Integer, db.ForeignKey("sale.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False, index=True)
    quantity = db.Column(db.Numeric(12, 2), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)

    sale = db.relationship("Sale", back_populates="items")
    product = db.relationship("Product")


class Payment(TenantAwareModel):
    __tablename__ = "payment"

    sale_id = db.Column(
        db.Integer, db.ForeignKey("sale.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cash_session_id = db.Column(
        db.Integer, db.ForeignKey("cash_session.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    method = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    reference = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="confirmed")

    sale = db.relationship("Sale", back_populates="payments")
    cash_session = db.relationship("CashSession", back_populates="payments")


class SalesTarget(TenantAwareModel):
    __tablename__ = "sales_target"

    year = db.Column(db.Integer, nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False, index=True)
    target_amount = db.Column(db.Numeric(12, 2), nullable=False)
    commercial_id = db.Column(db.Integer, db.ForeignKey("commercial.id"), nullable=True, index=True)
