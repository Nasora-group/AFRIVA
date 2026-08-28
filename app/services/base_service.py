"""Tenant-aware service primitives."""
from app.middleware.tenant_middleware import get_current_org_id


class BaseService:
    def __init__(self, repository):
        self.repo = repository

    def list_for_current_org(self, **filters):
        return self.repo.list_for_organization(get_current_org_id(), **filters)

    def get_for_current_org(self, entity_id):
        return self.repo.get_for_organization(get_current_org_id(), entity_id)

    def create_for_current_org(self, **kwargs):
        return self.repo.create_for_organization(get_current_org_id(), **kwargs)

    def soft_delete_for_current_org(self, entity_id):
        return self.repo.soft_delete_for_organization(get_current_org_id(), entity_id)
