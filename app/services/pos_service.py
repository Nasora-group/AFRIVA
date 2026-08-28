"""Business operations for POS cash sessions."""

from decimal import Decimal

from app.models import CashRegister, CashSession, db


class POSService:
    def open_session(self, register_id, opened_by, opening_amount=Decimal("0.00")):
        register = CashRegister.query.filter_by(id=register_id, active=True).first()
        if register is None:
            raise ValueError("Cash register not found in current organization")
        if opening_amount < 0:
            raise ValueError("opening_amount must be non-negative")
        existing = CashSession.query.filter_by(
            register_id=register_id, status="open"
        ).first()
        if existing is not None:
            raise ValueError("Cash register already has an open session")
        session = CashSession(
            register_id=register_id,
            opened_by=opened_by,
            opening_amount=opening_amount,
            status="open",
            organization_id=register.organization_id,
        )
        db.session.add(session)
        db.session.flush()
        return session

    def close_session(self, session_id, closed_by, closing_amount):
        session = CashSession.query.filter_by(id=session_id, status="open").first()
        if session is None:
            raise ValueError("Open cash session not found in current organization")
        closing_amount = Decimal(str(closing_amount))
        if closing_amount < 0:
            raise ValueError("closing_amount must be non-negative")
        session.closed_by = closed_by
        session.closing_amount = closing_amount
        session.closed_at = db.func.now()
        session.status = "closed"
        db.session.flush()
        return session
