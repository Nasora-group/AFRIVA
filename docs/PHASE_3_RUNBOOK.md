# AFRIVA Phase 3 — Runbook de validation

## 1. Créer une base PostgreSQL de TEST

Ne jamais utiliser la base de production.

```bash
export TEST_DATABASE_URL='postgresql://afriva:mot_de_passe@localhost:5432/afriva_test'
```

## 2. Installer les dépendances

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Exécuter la validation

```bash
export SECRET_KEY='test-only-secret'
./scripts/run_phase3_tests.sh
```

Sous Windows PowerShell :

```powershell
$env:TEST_DATABASE_URL='postgresql://afriva:mot_de_passe@localhost:5432/afriva_test'
$env:SECRET_KEY='test-only-secret'
pytest -v --cov=app --cov-report=term-missing --cov-fail-under=80
flake8 app tests
black --check app tests
isort --check-only app tests
```

## 4. CI

Le workflow `.github/workflows/ci.yml` crée automatiquement une PostgreSQL éphémère pour les Pull Requests et les pushes sur `main`.

## 5. RLS

La migration `002_phase3_rls.sql` active Row Level Security sur les tables tenant-aware du socle.

L'application doit définir le contexte dans la transaction :

```sql
SET LOCAL app.current_organization_id = '123';
```

Le rôle PostgreSQL utilisé par l'application ne doit pas être superuser.

## 6. Gate Phase 4

La Phase 4 ne commence que si :

- CI verte ;
- tests PostgreSQL Org A / Org B verts ;
- tests RBAC verts ;
- tests relations cross-tenant verts ;
- lint vert ;
- coverage >= 80 % ;
- migration validée sur une base de test ;
- aucune modification de production nécessaire pour cette validation.

**Aucune commande de migration de ce runbook ne cible la production.**
