"""Tenant-aware CRM models for Phase 4."""

from .base import TenantAwareModel, db, utcnow


class Commercial(TenantAwareModel):
    __tablename__ = "commercial"

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    active = db.Column(db.Boolean, nullable=False, default=True)


class Client(TenantAwareModel):
    __tablename__ = "client"

    name = db.Column(db.String(255), nullable=False)
    client_type = db.Column(db.String(50), nullable=False, default="business")
    sector = db.Column(db.String(100))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))
    status = db.Column(db.String(30), nullable=False, default="active", index=True)
    notes = db.Column(db.Text)


class Prospect(TenantAwareModel):
    __tablename__ = "prospect"

    name = db.Column(db.String(255), nullable=False)
    contact_name = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))
    status = db.Column(db.String(30), nullable=False, default="new", index=True)
    potential = db.Column(db.Numeric(14, 2))
    notes = db.Column(db.Text)


class Visit(TenantAwareModel):
    __tablename__ = "visit"

    commercial_id = db.Column(
        db.Integer,
        db.ForeignKey("commercial.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("client.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    prospect_id = db.Column(
        db.Integer,
        db.ForeignKey("prospect.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    visited_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utcnow
    )
    duration_minutes = db.Column(db.Integer)
    latitude = db.Column(db.Numeric(10, 7))
    longitude = db.Column(db.Numeric(10, 7))
    objective = db.Column(db.Text)
    result = db.Column(db.Text)
    notes = db.Column(db.Text)

    commercial = db.relationship("Commercial")
    client = db.relationship("Client")
    prospect = db.relationship("Prospect")


class Prospection(TenantAwareModel):
    __tablename__ = "prospection"

    commercial_id = db.Column(
        db.Integer,
        db.ForeignKey("commercial.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    prospect_id = db.Column(
        db.Integer,
        db.ForeignKey("prospect.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reason = db.Column(db.Text)
    interlocutor = db.Column(db.String(255))
    potential = db.Column(db.Numeric(14, 2))
    next_action = db.Column(db.Text)
    follow_up_at = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.String(30), nullable=False, default="open", index=True)
    notes = db.Column(db.Text)

    commercial = db.relationship("Commercial")
    prospect = db.relationship("Prospect")


class Tour(TenantAwareModel):
    __tablename__ = "tour"

    commercial_id = db.Column(
        db.Integer,
        db.ForeignKey("commercial.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(255), nullable=False)
    planned_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="planned", index=True)
    started_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))

    commercial = db.relationship("Commercial")
    stops = db.relationship(
        "TourStop",
        back_populates="tour",
        cascade="all, delete-orphan",
        order_by="TourStop.position",
    )


class TourStop(TenantAwareModel):
    __tablename__ = "tour_stop"

    tour_id = db.Column(
        db.Integer,
        db.ForeignKey("tour.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("client.id", ondelete="RESTRICT"),
        nullable=True,
    )
    prospect_id = db.Column(
        db.Integer,
        db.ForeignKey("prospect.id", ondelete="RESTRICT"),
        nullable=True,
    )
    position = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(30), nullable=False, default="planned")
    visited_at = db.Column(db.DateTime(timezone=True))
    notes = db.Column(db.Text)

    tour = db.relationship("Tour", back_populates="stops")
    client = db.relationship("Client")
    prospect = db.relationship("Prospect")


class Task(TenantAwareModel):
    __tablename__ = "crm_task"

    commercial_id = db.Column(
        db.Integer,
        db.ForeignKey("commercial.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("client.id", ondelete="RESTRICT"),
        nullable=True,
    )
    prospect_id = db.Column(
        db.Integer,
        db.ForeignKey("prospect.id", ondelete="RESTRICT"),
        nullable=True,
    )
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    status = db.Column(db.String(30), nullable=False, default="open", index=True)

    commercial = db.relationship("Commercial")
    client = db.relationship("Client")
    prospect = db.relationship("Prospect")


class Note(TenantAwareModel):
    __tablename__ = "crm_note"

    commercial_id = db.Column(
        db.Integer,
        db.ForeignKey("commercial.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    client_id = db.Column(
        db.Integer,
        db.ForeignKey("client.id", ondelete="RESTRICT"),
        nullable=True,
    )
    prospect_id = db.Column(
        db.Integer,
        db.ForeignKey("prospect.id", ondelete="RESTRICT"),
        nullable=True,
    )
    body = db.Column(db.Text, nullable=False)

    commercial = db.relationship("Commercial")
    client = db.relationship("Client")
    prospect = db.relationship("Prospect")
