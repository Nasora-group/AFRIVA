# AFRIVA — Phase 3 Status

## Socle multi-tenant

### Implémenté

- Flask application factory
- SQLAlchemy extension
- Environment-only configuration
- Organization model
- User model
- OrganizationUser membership
- Organization-scoped Role
- Global Permission catalog
- ActivityLog audit model
- Tenant context middleware
- Session authentication foundation
- Tenant-aware repository base
- Tenant-aware service base
- RBAC decorator
- Soft-delete primitive
- PostgreSQL foundation migration
- PostgreSQL RLS defense-in-depth migration
- PostgreSQL integration test suite
- CI with PostgreSQL service
- pytest + coverage gate
- flake8 / black / isort CI gates
- reproducible Phase 3 test script
- Phase 3 validation runbook

### Sécurité

- `organization_id` obligatoire pour les modèles tenant-aware
- le tenant courant provient du contexte serveur/session et d'une affiliation active
- les IDs d'organisation fournis par les formulaires/API ne définissent pas le tenant
- les repositories filtrent par tenant
- les créations imposent le tenant du contexte
- les relations doivent être validées dans le même tenant avant toute opération métier
- aucune suppression physique des données métier via le repository
- PostgreSQL RLS fournit une seconde barrière pour le socle tenant-aware
- les tests d'intégration utilisent exclusivement `TEST_DATABASE_URL`
- la CI utilise une PostgreSQL éphémère et ne possède aucun secret de production

### Validation opérationnelle

Le socle est implémenté et les derniers commits ont porté sur la conformité de formatage Python. La validation finale est exécutée par GitHub Actions sur cette branche/PR avec PostgreSQL éphémère.

Runbook : `docs/PHASE_3_RUNBOOK.md`

### Gate avant Phase 4

La Phase 4 CRM/POS/Stock ne doit commencer que lorsque GitHub Actions confirme :

- [ ] tests verts ;
- [ ] coverage >= 80 % ;
- [ ] lint vert ;
- [ ] tests PostgreSQL Org A / Org B verts ;
- [ ] RLS validée ;
- [ ] aucun accès cross-tenant ;
- [ ] aucune commande exécutée contre la production.

**Statut : SOCLE PHASE 3 — VALIDATION CI EN COURS.**
