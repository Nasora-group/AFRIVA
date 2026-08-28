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
- Authentication primitives
- Tenant-aware repository base
- Tenant-aware service base
- RBAC decorator
- Soft-delete primitive
- Pytest foundation
- Cross-tenant contract tests
- `.env.example`
- `.gitignore`

### Sécurité

- `organization_id` obligatoire pour les modèles tenant-aware
- le tenant courant provient du contexte serveur/session et d'une affiliation active
- les IDs d'organisation fournis par les formulaires/API ne définissent pas le tenant
- les repositories filtrent par tenant
- les créations imposent le tenant du contexte
- les relations doivent être validées dans le même tenant avant toute opération métier
- aucune suppression physique des données métier via le repository

### Validation finale encore requise avant Phase 4

1. Brancher un provider d'authentification réel et sécurisé.
2. Générer et exécuter les migrations Alembic contre une PostgreSQL de test.
3. Remplacer les contract tests par des tests d'intégration DB complets Org A / Org B.
4. Ajouter les tests RBAC et relations cross-tenant.
5. Ajouter CI avec pytest + coverage + lint.
6. Activer PostgreSQL RLS en défense en profondeur après validation du schéma.

**Important :** la Phase 3 code-first est en place, mais la phase ne doit être déclarée totalement sécurisée qu'après l'exécution des tests PostgreSQL réels dans CI. Aucun module métier ne doit contourner ces contrôles.
