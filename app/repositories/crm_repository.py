"""Tenant-aware repositories for CRM entities."""

from app.middleware.tenant_middleware import get_current_organization
from app.models import Client, Commercial, Prospect, Prospection, Tour, Visit, db


class TenantRepository:
    model = None

    def __init__(self, model=None):
        if model is not None:
            self.model = model

    def _organization_id(self):
        organization = get_current_organization()
        if organization is None:
            raise RuntimeError("No current organization in request context")
        return organization.id

    def query(self):
        return self.model.query.filter_by(organization_id=self._organization_id())

    def get(self, entity_id):
        return self.query().filter_by(id=entity_id).first()

    def list(self, limit=100, offset=0):
        return self.query().order_by(self.model.id.desc()).offset(offset).limit(limit).all()

    def add(self, entity):
        entity.organization_id = self._organization_id()
        db.session.add(entity)
        db.session.flush()
        return entity


class CommercialRepository(TenantRepository):
    model = Commercial


class ClientRepository(TenantRepository):
    model = Client


class ProspectRepository(TenantRepository):
    model = Prospect


class VisitRepository(TenantRepository):
    model = Visit


class ProspectionRepository(TenantRepository):
    model = Prospection


class TourRepository(TenantRepository):
    model = Tour
