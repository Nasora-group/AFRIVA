"""Tenant-aware repository primitives."""
from app.models.base import db


class BaseRepository:
    model = None

    def get_for_organization(self, org_id, entity_id):
        return self.model.query.filter(
            self.model.organization_id == org_id,
            self.model.id == entity_id,
            self.model.deleted_at.is_(None),
        ).first()

    def list_for_organization(self, org_id, **filters):
        query = self.model.query.filter(
            self.model.organization_id == org_id,
            self.model.deleted_at.is_(None),
        )
        for key, value in filters.items():
            if not hasattr(self.model, key) or key == "organization_id":
                continue
            query = query.filter(getattr(self.model, key) == value)
        return query.all()

    def create_for_organization(self, org_id, **kwargs):
        # Never allow caller input to override the security boundary.
        kwargs.pop("organization_id", None)
        entity = self.model(organization_id=org_id, **kwargs)
        db.session.add(entity)
        db.session.flush()
        return entity

    def soft_delete_for_organization(self, org_id, entity_id):
        entity = self.get_for_organization(org_id, entity_id)
        if entity is None:
            return None
        from app.models.base import utcnow
        entity.deleted_at = utcnow()
        db.session.flush()
        return entity
