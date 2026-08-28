"""CRM domain models for AFRIVA."""

from datetime import date, datetime

from .base import TenantAwareModel, db


class Commercial(TenantAwareModel):
    __tablename__ = "commercial"

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    clients = db.relationship("Client", back_populates="commercial")
    prospects = db.relationship("Prospect", back_populates="commercial")
    visits = db.relationship("Visit", back_populates="commercial")
    prospections = db.relationship("Prospection", back_populates="commercial")


class Client(TenantAwareModel):
    __tablename__ = "client"

    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    commercial_id = db.Column(
        db.Integer,
        db.ForeignKey("commercial.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    commercial = db.relationship("Commercial", back_populates="clients")
    visits = db.relationship("Visit", back_populates="client")


class Prospect(TenantAwareModel):
    __tablename__ = "prospect"

    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="new")
    commercial_id = db.Column(
        db.Integer,
        db.ForeignKey("commercial.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    commercial = db.relationship("Commercial", back_populates="prospects")
    visits = db.relationship("Visit", back_populates="prospect")


class Contact(TenantAwareModel):
    __tablename__ = "contact"

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey("client.id", ondelete="CASCADE"), nullable=True
    )
    prospect_id = db.Column(
        db.Integer, db.ForeignKey("prospect.id", ondelete="CASCADE"), nullable=True
    )


class Visit(TenantAwareModel):
    __tablename__ = "visit"

    visited_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    commercial_id = db.Column(db.Integer, db.ForeignKey("commercial.id"), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=True, index=True)
    prospect_id = db.Column(db.Integer, db.ForeignKey("prospect.id"), nullable=True, index=True)

    commercial = db.relationship("Commercial", back_populates="visits")
    client = db.relationship("Client", back_populates="visits")
    prospect = db.relationship("Prospect", back_populates="visits")


class Prospection(TenantAwareModel):
    __tablename__ = "prospection"

    visited_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    outcome = db.Column(db.String(100), nullable=False, default="pending")
    notes = db.Column(db.Text, nullable=True)
    commercial_id = db.Column(db.Integer, db.ForeignKey("commercial.id"), nullable=False, index=True)
    prospect_id = db.Column(db.Integer, db.ForeignKey("prospect.id"), nullable=True, index=True)

    commercial = db.relationship("Commercial", back_populates="prospections")


class Tour(TenantAwareModel):
    __tablename__ = "tour"

    name = db.Column(db.String(255), nullable=False)
    tour_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    commercial_id = db.Column(db.Integer, db.ForeignKey("commercial.id"), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default="planned")

    stops = db.relationship("TourStop", back_populates="tour", cascade="all, delete-orphan")


class TourStop(TenantAwareModel):
    __tablename__ = "tour_stop"

    sequence = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="planned")
    planned_at = db.Column(db.DateTime(timezone=True), nullable=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    tour_id = db.Column(db.Integer, db.ForeignKey("tour.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=True, index=True)
    prospect_id = db.Column(db.Integer, db.ForeignKey("prospect.id"), nullable=True, index=True)

    tour = db.relationship("Tour", back_populates="stops")
