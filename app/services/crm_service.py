"""Application services for CRM operations."""

from app.models import Client, Contact, Prospect, Prospection, Tour, TourStop, Visit, db
from app.repositories.crm_repository import (
    ClientRepository,
    CommercialRepository,
    ContactRepository,
    ProspectRepository,
    ProspectionRepository,
    TourRepository,
    TourStopRepository,
    VisitRepository,
)


class CRMService:
    def __init__(self):
        self.commercials = CommercialRepository()
        self.clients = ClientRepository()
        self.prospects = ProspectRepository()
        self.contacts = ContactRepository()
        self.visits = VisitRepository()
        self.prospections = ProspectionRepository()
        self.tours = TourRepository()
        self.tour_stops = TourStopRepository()

    def create_client(self, **data):
        return self.clients.add(Client(**data))

    def create_prospect(self, **data):
        return self.prospects.add(Prospect(**data))

    def create_contact(self, **data):
        if data.get("client_id") is not None and self.clients.get(data["client_id"]) is None:
            raise ValueError("Client not found in current organization")
        if data.get("prospect_id") is not None and self.prospects.get(data["prospect_id"]) is None:
            raise ValueError("Prospect not found in current organization")
        return self.contacts.add(Contact(**data))

    def record_visit(self, commercial_id, client_id=None, prospect_id=None, **data):
        commercial = self.commercials.get(commercial_id)
        if commercial is None:
            raise ValueError("Commercial not found in current organization")
        if client_id is not None and self.clients.get(client_id) is None:
            raise ValueError("Client not found in current organization")
        if prospect_id is not None and self.prospects.get(prospect_id) is None:
            raise ValueError("Prospect not found in current organization")
        return self.visits.add(Visit(commercial_id=commercial_id, client_id=client_id, prospect_id=prospect_id, **data))

    def record_prospection(self, commercial_id, prospect_id=None, **data):
        if self.commercials.get(commercial_id) is None:
            raise ValueError("Commercial not found in current organization")
        if prospect_id is not None and self.prospects.get(prospect_id) is None:
            raise ValueError("Prospect not found in current organization")
        return self.prospections.add(Prospection(commercial_id=commercial_id, prospect_id=prospect_id, **data))

    def create_tour(self, commercial_id, **data):
        if self.commercials.get(commercial_id) is None:
            raise ValueError("Commercial not found in current organization")
        return self.tours.add(Tour(commercial_id=commercial_id, **data))

    def add_tour_stop(self, tour_id, client_id=None, prospect_id=None, **data):
        if self.tours.get(tour_id) is None:
            raise ValueError("Tour not found in current organization")
        if client_id is not None and self.clients.get(client_id) is None:
            raise ValueError("Client not found in current organization")
        if prospect_id is not None and self.prospects.get(prospect_id) is None:
            raise ValueError("Prospect not found in current organization")
        return self.tour_stops.add(TourStop(tour_id=tour_id, client_id=client_id, prospect_id=prospect_id, **data))

    def commit(self):
        db.session.commit()
