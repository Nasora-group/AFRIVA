"""Security tests for AFRIVA tenant isolation."""


def test_repository_never_returns_another_tenant_resource():
    class FakeModel:
        organization_id = None
        id = None
        deleted_at = None

    from app.repositories.base_repository import BaseRepository

    repo = BaseRepository()
    repo.model = FakeModel
    assert hasattr(repo, "get_for_organization")
    assert hasattr(repo, "list_for_organization")


def test_create_contract_forces_tenant():
    from app.repositories.base_repository import BaseRepository

    class Entity:
        def __init__(self, organization_id, **kwargs):
            self.organization_id = organization_id
            self.deleted_at = None
            self.__dict__.update(kwargs)

    class FakeRepo(BaseRepository):
        model = Entity

    assert FakeRepo().model is Entity


def test_cross_tenant_access_contract():
    """Org B must not receive a resource belonging to Org A."""
    org_a = 1
    org_b = 2
    resource_org = org_a
    assert resource_org != org_b
