"""Application services for CRM operations."""

from app.models import Client, Prospect, Prospection, Visit, db
from app.repositories.crm_repository import (
    ClientRepository,
    CommercialRepository,
    ProspectRepository,
    ProspectionRepository,
    TourRepository,
    VisitRepository,
)


class CRMService:
    def __init__(self):
        self.commercials = CommercialRepository()
        self.clients = ClientRepository()
        self.prospects = ProspectRepository()
        self.visits = VisitRepository()
        self.prospections = ProspectionRepository()
        self.tours = TourRepository()

    def create_client(self, **data):
        return self.clients.add(Client(**data))

    def create_prospect(self, **data):
        return self.prospects.add(Prospect(**data))

    def record_visit(self, commercial_id, client_id=None, prospect_id=None, **data):
        commercial = self.commercials.get(commercial_id)
        if commercial is None:
            raise ValueError("Commercial not found in current organization")
        if client_id is not None and self.clients.get(client_id) is None:
            raise ValueError("Client not found in current organization")
        if prospect_id is not None and self.prospects.get(prospect_id) is None:
            raise ValueError("Prospect not found in current organization")
        return self.visits.add(
            Visit(
                commercial_id=commercial_id,
                client_id=client_id,
                prospect_id=prospect_id,
                **data,
            )
        )

    def record_prospection(self, commercial_id, prospect_id=None, **data):
        if self.commercials.get(commercial_id) is None:
            raise ValueError("Commercial not found in current organization")
        if prospect_id is not None and self.prospects.get(prospect_id) is None:
            raise ValueError("Prospect not found in current organization")
        return self.prospections.add(
            Prospection(
                commercial_id=commercial_id,
                prospect_id=prospect_id,
                **data,
            )
        )

    def commit(self):
        db.session.commit()
