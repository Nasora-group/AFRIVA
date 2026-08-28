"""Tenant organization model."""
from .base import db, BaseModel


class Organization(BaseModel):
    __tablename__ = "organization"

    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    logo = db.Column(db.String(500))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100), default="Senegal")
    currency = db.Column(db.String(3), default="XOF", nullable=False)
    timezone = db.Column(db.String(50), default="Africa/Dakar", nullable=False)
    industry = db.Column(db.String(100))
    status = db.Column(db.String(50), default="trial", nullable=False, index=True)
