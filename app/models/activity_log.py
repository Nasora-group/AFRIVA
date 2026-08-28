"""Immutable audit trail for security-sensitive actions."""
from .base import db, BaseModel


class ActivityLog(BaseModel):
    __tablename__ = "activity_log"

    organization_id = db.Column(
        db.Integer, db.ForeignKey("organization.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="RESTRICT"), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    resource_type = db.Column(db.String(100), nullable=False)
    resource_id = db.Column(db.Integer, nullable=True, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    metadata_json = db.Column(db.JSON, nullable=True)
