"""Global users and tenant memberships."""

from .base import BaseModel, db


class User(BaseModel):
    __tablename__ = "user"

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    status = db.Column(db.String(50), default="active", nullable=False)

    organization_users = db.relationship(
        "OrganizationUser", back_populates="user", cascade="save-update, merge"
    )


class OrganizationUser(BaseModel):
    __tablename__ = "organization_user"
    __table_args__ = (
        db.UniqueConstraint("user_id", "organization_id", name="uq_user_organization"),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    organization_id = db.Column(
        db.Integer,
        db.ForeignKey("organization.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    role_id = db.Column(
        db.Integer,
        db.ForeignKey("role.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status = db.Column(db.String(50), default="active", nullable=False, index=True)

    user = db.relationship("User", back_populates="organization_users")
    organization = db.relationship("Organization", backref=db.backref("memberships", lazy=True))
    role = db.relationship("Role", back_populates="memberships")
