"""Point-of-sale and cash management models."""

from datetime import datetime, timezone
from decimal import Decimal

from .base import TenantAwareModel, db


class Store(TenantAwareModel):
    __tablename__ = "store"

    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    registers = db.relationship("CashRegister", back_populates="store", cascade="all, delete-orphan")


class CashRegister(TenantAwareModel):
    __tablename__ = "cash_register"

    store_id = db.Column(db.Integer, db.ForeignKey("store.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(100), nullable=False, index=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    store = db.relationship("Store", back_populates="registers")
    sessions = db.relationship("CashSession", back_populates="register", cascade="all, delete-orphan")


class CashSession(TenantAwareModel):
    __tablename__ = "cash_session"

    register_id = db.Column(db.Integer, db.ForeignKey("cash_register.id", ondelete="RESTRICT"), nullable=False, index=True)
    opened_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="RESTRICT"), nullable=False)
    closed_by = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="RESTRICT"), nullable=True)
    opened_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    closed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    opening_amount = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    closing_amount = db.Column(db.Numeric(12, 2), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="open", index=True)

    register = db.relationship("CashRegister", back_populates="sessions")
