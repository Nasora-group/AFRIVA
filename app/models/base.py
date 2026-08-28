"""Base SQLAlchemy models used by AFRIVA."""

from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class TenantAwareModel(BaseModel):
    __abstract__ = True

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey("organization.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
