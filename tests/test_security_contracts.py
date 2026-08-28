"""Phase 3 security contracts; no production database is used."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tenant_repository_contains_security_filter():
    text = (ROOT / "app/repositories/base_repository.py").read_text()
    assert "self.model.organization_id == org_id" in text
    assert "kwargs.pop(\"organization_id\", None)" in text


def test_no_physical_delete_in_app():
    offenders = []
    for path in (ROOT / "app").rglob("*.py"):
        text = path.read_text()
        if "db.session.delete(" in text:
            offenders.append(str(path))
    assert offenders == []


def test_required_permissions_exist():
    text = (ROOT / "app/models/role.py").read_text()
    for permission in ("clients.view", "sales.create", "pos.sell", "inventory.adjust", "reports.export"):
        assert permission in text


def test_secrets_are_environment_based():
    text = (ROOT / "app/config.py").read_text()
    assert 'os.getenv("DATABASE_URL")' in text
    assert 'os.getenv("SECRET_KEY")' in text
