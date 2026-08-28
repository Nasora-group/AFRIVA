"""RBAC models. Permissions are global; roles belong to an organization."""

from .base import BaseModel, TenantAwareModel, db

role_permission = db.Table(
    "role_permission",
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("role.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "permission_id",
        db.Integer,
        db.ForeignKey("permission.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class Role(TenantAwareModel):
    __tablename__ = "role"

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    permissions = db.relationship(
        "Permission", secondary=role_permission, lazy="selectin"
    )
    memberships = db.relationship("OrganizationUser", back_populates="role")


class Permission(BaseModel):
    __tablename__ = "permission"

    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)


DEFAULT_PERMISSIONS = (
    "clients.view",
    "clients.create",
    "clients.update",
    "clients.delete",
    "sales.view",
    "sales.create",
    "sales.update",
    "sales.cancel",
    "pos.open",
    "pos.sell",
    "pos.discount",
    "pos.close",
    "inventory.view",
    "inventory.adjust",
    "inventory.transfer",
    "reports.view",
    "reports.export",
    "users.create",
    "users.update",
    "users.delete",
)
