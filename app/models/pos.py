"""Point-of-sale models for Phase 6."""

from decimal import Decimal

from .base import TenantAwareModel, db, utcnow


class Store(TenantAwareModel):
    __tablename__ = "store"

    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.String(500))
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)


class POSRegister(TenantAwareModel):
    __tablename__ = "pos_register"

    store_id = db.Column(
        db.Integer,
        db.ForeignKey("store.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), nullable=False, index=True)
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    store = db.relationship("Store")


class CashSession(TenantAwareModel):
    __tablename__ = "cash_session"

    register_id = db.Column(
        db.Integer,
        db.ForeignKey("pos_register.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    opened_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="RESTRICT"),
        nullable=False,
    )
    closed_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="RESTRICT"),
        nullable=True,
    )
    opened_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    closed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    opening_cash = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0"))
    closing_cash = db.Column(db.Numeric(14, 2), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="open", index=True)
    register = db.relationship("POSRegister")


class POSSale(TenantAwareModel):
    __tablename__ = "pos_sale"

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("cash_session.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reference = db.Column(db.String(100), nullable=False, unique=True, index=True)
    sold_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utcnow, index=True
    )
    status = db.Column(db.String(20), nullable=False, default="confirmed", index=True)
    total_amount = db.Column(db.Numeric(14, 2), nullable=False, default=Decimal("0"))
    session = db.relationship("CashSession")
    lines = db.relationship(
        "POSSaleLine", back_populates="sale", cascade="all, delete-orphan"
    )
    payments = db.relationship(
        "POSPayment", back_populates="sale", cascade="all, delete-orphan"
    )


class POSSaleLine(TenantAwareModel):
    __tablename__ = "pos_sale_line"

    sale_id = db.Column(
        db.Integer,
        db.ForeignKey("pos_sale.id", ondelete="CASCADE"),
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
    unit_price = db.Column(db.Numeric(14, 2), nullable=False)
    line_total = db.Column(db.Numeric(14, 2), nullable=False)
    sale = db.relationship("POSSale", back_populates="lines")
    product = db.relationship("Product")


class POSPayment(TenantAwareModel):
    __tablename__ = "pos_payment"

    sale_id = db.Column(
        db.Integer,
        db.ForeignKey("pos_sale.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    method = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    paid_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    sale = db.relationship("POSSale", back_populates="payments")
