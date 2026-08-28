import pytest

from app.models import Client, Organization, db
from app.repositories.crm_repository import ClientRepository


def test_repository_requires_tenant(app):
    with app.app_context():
        with pytest.raises(RuntimeError, match="No current organization"):
            ClientRepository().list()


def test_repository_scopes_by_current_tenant(app, monkeypatch):
    with app.app_context():
        org_a = Organization(name="A", slug="org-a")
        org_b = Organization(name="B", slug="org-b")
        db.session.add_all([org_a, org_b])
        db.session.flush()
        db.session.add_all(
            [
                Client(name="A client", organization_id=org_a.id),
                Client(name="B client", organization_id=org_b.id),
            ]
        )
        db.session.commit()

        monkeypatch.setattr(
            "app.repositories.crm_repository.get_current_organization", lambda: org_a
        )
        results = ClientRepository().list()
        assert [item.name for item in results] == ["A client"]
        assert ClientRepository().get(999999) is None
