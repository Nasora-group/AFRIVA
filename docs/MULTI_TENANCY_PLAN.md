# AFRIVA SaaS — Plan d'architecture Multi-Tenant

**Phase :** 2 — Architecture Multi-Tenant  
**Date :** 28 août 2026  
**Statut :** Validé pour implémentation  
**Modèle :** Shared Database / Shared Schema  
**Principe fondamental :** aucune donnée d'une organization ne doit être accessible par une autre.

---

## 1. Objectif

Ce document définit le socle d'isolation des données d'AFRIVA SaaS avant l'implémentation du code applicatif.

AFRIVA doit permettre à plusieurs entreprises clientes de partager la même application et la même base PostgreSQL tout en conservant une isolation stricte de leurs données.

```text
                    AFRIVA SaaS
                         │
          ┌──────────────┼──────────────┐
          │              │              │
       Org A           Org B          Org C
          │              │              │
       données        données        données
       isolées        isolées        isolées
          └──────────────┼──────────────┘
                         │
                  PostgreSQL
              Shared Database
               Shared Schema
```

L'identité de l'organisation courante ne doit **jamais** être déterminée uniquement à partir d'une valeur fournie par le navigateur ou l'API.

---

## 2. Principes non négociables

### P1 — Tenant context obligatoire

Toute requête authentifiée doit posséder un contexte `current_organization` avant d'accéder aux données tenant-aware.

### P2 — `organization_id` obligatoire

Toute entité appartenant à une entreprise doit avoir un `organization_id` non nullable.

Exceptions : données réellement globales à AFRIVA, notamment les plans SaaS et permissions globales.

### P3 — Pas de confiance dans l'URL

Interdit comme mécanisme d'autorisation :

```text
GET /api/v1/organizations/999/clients
```

Le serveur doit déterminer le tenant depuis l'utilisateur authentifié et vérifier son affiliation.

### P4 — Repository tenant-aware obligatoire

Les accès aux modèles tenant-owned passent par des repositories ou services qui imposent le tenant.

### P5 — RBAC après tenant context

L'ordre est :

```text
Authentication
→ Tenant Context
→ Membership
→ Permission
→ Resource Access
```

### P6 — Audit

Toute opération sensible est journalisée avec `organization_id` et `user_id`.

### P7 — Soft delete

Aucune suppression physique des données métier sensibles.

### P8 — Tests cross-tenant obligatoires

Chaque nouvelle entité tenant-aware doit posséder des tests prouvant qu'un utilisateur d'Org B ne peut ni lire ni modifier les données d'Org A.

---

## 3. Classification des données

### 3.1 Données globales AFRIVA

Ces données ne sont pas rattachées à une organization :

```text
Permission
Plan SaaS
Paramètres système globaux
```

Elles doivent néanmoins être protégées par RBAC lorsqu'elles sont administrables.

### 3.2 Données tenant-aware

Toutes les données métier des entreprises clientes :

```text
Client
Prospect
Contact
Commercial
Visit
Prospection
Tour

Sale
SaleItem
Objective
Performance

Store
CashRegister
CashSession
POS Sale
POS SaleItem
Payment
Receipt
CashIn
CashOut

Product
ProductStock
StockMovement
Inventory
ProductBatch
StockTransfer

Subscription
Invoice
BillingPayment
ActivityLog
```

### 3.3 Cas particulier Users

`User` représente l'identité globale.

Le rattachement à une entreprise est porté par :

```text
OrganizationUser
```

Ainsi un même utilisateur peut appartenir à plusieurs organizations.

---

## 4. Modèle d'identité

```text
                    User
                     │
          ┌──────────┴──────────┐
          │                     │
 OrganizationUser          OrganizationUser
          │                     │
       Org A                  Org B
          │                     │
        Role A                Role B
```

### User

Responsable de l'identité globale :

- email unique ;
- mot de passe hashé ;
- prénom ;
- nom ;
- statut ;
- MFA éventuel.

### OrganizationUser

Responsable de l'appartenance :

- `user_id` ;
- `organization_id` ;
- `role_id` ;
- statut de l'affiliation ;
- timestamps.

Contrainte obligatoire :

```text
UNIQUE(user_id, organization_id)
```

### Organization

Contient le tenant :

- nom ;
- slug ;
- coordonnées ;
- devise ;
- timezone ;
- secteur ;
- statut ;
- plan SaaS.

---

## 5. Tenant Context

Le contexte tenant est créé côté serveur.

```python
@app.before_request
def load_tenant_context():
    user = get_current_user()

    if not user:
        return

    org_id = session.get("current_org_id")

    if org_id is None:
        memberships = get_active_memberships(user.id)
        if not memberships:
            abort(403)
        org_id = memberships[0].organization_id

    membership = OrganizationUser.query.filter_by(
        user_id=user.id,
        organization_id=org_id,
        status="active",
    ).first()

    if membership is None:
        abort(403)

    g.current_organization = membership.organization
    g.current_org_id = membership.organization_id
    g.current_membership = membership
```

### API du contexte

```python
def get_current_organization():
    org = getattr(g, "current_organization", None)
    if org is None:
        abort(403)
    return org


def get_current_org_id():
    org_id = getattr(g, "current_org_id", None)
    if org_id is None:
        abort(403)
    return org_id
```

### Interdiction

Ne jamais utiliser :

```python
request.args.get("organization_id")
request.json.get("organization_id")
request.view_args.get("organization_id")
```

pour établir le tenant de confiance.

Une valeur `organization_id` envoyée par le client peut être utilisée uniquement dans un cas fonctionnel explicite et doit être validée contre le contexte et les droits de l'utilisateur.

---

## 6. Changement d'organization

Si un utilisateur appartient à plusieurs organizations :

```text
User connecté
      ↓
GET organizations accessibles
      ↓
Choix Org B
      ↓
Vérification OrganizationUser
      ↓
Session current_org_id = Org B
      ↓
Nouveau contexte tenant
```

Le changement doit être audité :

```text
action = switch_organization
```

Un utilisateur suspendu ou supprimé de l'organization ne doit plus pouvoir utiliser son ancien `current_org_id`.

---

## 7. Repository tenant-aware

Le repository est une barrière obligatoire contre les oublis de filtre.

```python
class BaseRepository:
    model = None

    def get_for_organization(self, org_id, entity_id):
        return self.model.query.filter(
            self.model.organization_id == org_id,
            self.model.id == entity_id,
        ).first()

    def list_for_organization(self, org_id, **filters):
        query = self.model.query.filter(
            self.model.organization_id == org_id
        )

        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(
                    getattr(self.model, key) == value
                )

        return query.all()

    def create_for_organization(self, org_id, **kwargs):
        kwargs["organization_id"] = org_id
        entity = self.model(**kwargs)
        db.session.add(entity)
        db.session.commit()
        return entity
```

### Règle supplémentaire

Le repository ne doit pas accepter silencieusement un `organization_id` fourni dans `kwargs` différent du tenant courant.

Idéalement, l'API publique du repository reçoit `org_id` séparément et écrase toute valeur externe.

---

## 8. Service tenant-aware

```python
class BaseService:
    def __init__(self, repository):
        self.repo = repository

    def list_for_current_org(self, **filters):
        org_id = get_current_org_id()
        return self.repo.list_for_organization(org_id, **filters)

    def get_for_current_org(self, entity_id):
        org_id = get_current_org_id()
        return self.repo.get_for_organization(org_id, entity_id)

    def create_for_current_org(self, **kwargs):
        org_id = get_current_org_id()
        return self.repo.create_for_organization(org_id, **kwargs)
```

Les routes doivent rester fines : elles valident la requête et délèguent au service.

---

## 9. RBAC

La permission doit être évaluée dans le contexte de l'affiliation courante.

```python
@require_permission("clients.create")
def create_client():
    ...
```

Mais `require_permission` doit utiliser le `current_membership` de la requête et non un rôle global arbitraire.

### Flux

```text
User
 ↓
Current Organization
 ↓
OrganizationUser
 ↓
Role
 ↓
Permission
```

Un rôle d'Org A ne doit jamais autoriser implicitement une opération dans Org B.

---

## 10. Matrice de permissions minimale

```text
clients.view
clients.create
clients.update
clients.delete

prospects.view
prospects.create
prospects.update
prospects.delete

sales.view
sales.create
sales.update
sales.cancel

pos.open
pos.sell
pos.discount
pos.close

inventory.view
inventory.adjust
inventory.transfer

reports.view
reports.export

users.create
users.update
users.delete
```

Des permissions supplémentaires pourront être ajoutées par module sans casser le modèle.

---

## 11. Relations cross-tenant

Le simple fait que l'entité principale ait le bon `organization_id` ne suffit pas.

Exemple : création d'une vente :

```text
Sale.organization_id = current_org.id
Customer.organization_id = current_org.id
Commercial.organization_id = current_org.id
Product.organization_id = current_org.id
Store.organization_id = current_org.id
```

Toute relation entrante doit être validée.

### Exemple

Interdit :

```python
product = Product.query.get(product_id)
```

Puis utiliser ce produit dans une vente de l'Org A.

Correct :

```python
product = Product.query.filter_by(
    id=product_id,
    organization_id=current_org.id,
).first()
```

---

## 12. POS : isolation renforcée

Le POS est particulièrement sensible car il combine plusieurs écritures.

Une vente POS doit vérifier :

```text
Organization
 ↓
Store
 ↓
CashRegister
 ↓
CashSession
 ↓
Product / Stock
 ↓
Payment
```

Une caisse appartenant à Org B ne doit jamais pouvoir être utilisée pour une vente d'Org A.

### Transaction

La création d'une vente POS doit être atomique :

```text
BEGIN
  créer POS Sale
  créer SaleItems
  décrémenter stock
  enregistrer Payment
  mettre à jour CashSession
  créer Receipt
  créer ActivityLog
COMMIT
```

En cas d'erreur : `ROLLBACK` de toutes les opérations.

---

## 13. Stock : isolation renforcée

Un `ProductStock` doit toujours être lié à un produit et à un magasin du même tenant.

```text
Product.organization_id
        ==
ProductStock.organization_id
        ==
Store.organization_id
        ==
current_org.id
```

Pour un transfert :

```text
Source Store → Org A
Destination Store → Org A
```

Tout transfert inter-tenant est interdit.

---

## 14. Audit Trail multi-tenant

`ActivityLog` doit être tenant-aware :

```text
organization_id
user_id
action
resource_type
resource_id
ip_address
user_agent
metadata JSONB
created_at
```

### Règle

Le log ne doit jamais pouvoir être créé avec une organization différente du contexte courant pour une opération utilisateur.

Les opérations système exceptionnelles doivent utiliser un mécanisme explicite de service account et être identifiables dans l'audit.

---

## 15. Soft Delete

Les données métier ne doivent pas être physiquement supprimées.

Exemples :

```python
client.deleted_at = datetime.utcnow()
```

ou statut métier :

```python
sale.status = "cancelled"
```

Une annulation de vente doit déclencher les compensations métier nécessaires et être auditée.

---

## 16. PostgreSQL et RLS

### Niveau 1 — Application

Obligatoire dès la Phase 3 :

- tenant context ;
- repositories ;
- services ;
- RBAC ;
- tests.

### Niveau 2 — Base de données

À mettre en place après stabilisation du schéma : PostgreSQL Row Level Security.

Concept cible :

```text
PostgreSQL session
      ↓
SET LOCAL app.current_organization_id = '123'
      ↓
RLS policy
      ↓
organization_id = current tenant
```

RLS doit être considéré comme **défense en profondeur**, pas comme remplacement des contrôles applicatifs.

---

## 17. Indexation

Toutes les tables tenant-aware fortement consultées doivent disposer d'un index sur `organization_id`.

Pour les requêtes fréquentes, préférer des indexes composites :

```text
(organization_id, status)
(organization_id, created_at)
(organization_id, commercial_id)
(organization_id, store_id)
(organization_id, product_id)
```

Les indexes seront déterminés précisément à partir des requêtes réelles et des plans PostgreSQL.

---

## 18. Pagination obligatoire

Les listes tenant-aware ne doivent pas charger une quantité illimitée de données.

Interdit à terme :

```python
Client.query.filter_by(organization_id=org_id).all()
```

pour des écrans potentiellement volumineux.

Préférer :

```text
page
page_size
cursor éventuel
```

avec une limite maximale côté serveur.

---

## 19. API REST sécurisée

Chaque endpoint doit suivre exactement ce pipeline :

```text
HTTP Request
    ↓
Authentication
    ↓
Tenant Context
    ↓
RBAC
    ↓
Input Validation
    ↓
Service
    ↓
Tenant-aware Repository
    ↓
DB Transaction
    ↓
Audit Log
    ↓
JSON Response
```

### Erreurs

Ne pas révéler d'informations cross-tenant.

Par exemple, lorsqu'un ID appartient à Org B, l'API ne doit pas retourner :

```text
"La ressource existe mais appartient à Org B"
```

Elle doit utiliser une réponse contrôlée, typiquement `404` pour masquer l'existence, selon le contexte de l'endpoint.

---

## 20. Tests obligatoires

### Test 1 — Lecture cross-tenant

```python
def test_organization_isolation(client, org_a, org_b):
    resource = create_client_for_org(org_a)

    authenticate_as_org(org_b)

    response = client.get(f"/api/v1/clients/{resource.id}")

    assert response.status_code in (403, 404)
```

### Test 2 — Modification cross-tenant

```python
def test_cross_tenant_update_forbidden(...):
    ...
```

### Test 3 — Suppression/annulation cross-tenant

```python
def test_cross_tenant_delete_forbidden(...):
    ...
```

### Test 4 — Relation cross-tenant

Org A ne doit pas pouvoir créer une vente en utilisant un produit, client, magasin ou commercial de Org B.

### Test 5 — Changement de tenant

Un utilisateur multi-org ne doit accéder qu'aux données de l'organisation actuellement sélectionnée.

### Test 6 — Session expirée / membership révoqué

Un `current_org_id` ancien ne doit pas permettre l'accès après révocation de l'affiliation.

### Test 7 — RBAC

Un utilisateur authentifié sans permission doit recevoir `403` même s'il connaît l'URL exacte.

### Test 8 — Pagination

Vérifier qu'une requête ne peut pas contourner les limites pour récupérer les données d'un autre tenant.

---

## 21. Migration des données

### Situation actuelle

L'audit Phase 1 a établi que le repository actuel est une ossature documentaire et ne contient pas encore de schéma applicatif SQLAlchemy/Alembic à migrer. La migration sera donc construite comme une fondation propre. fileciteturn0file0

### Si une base existante est introduite ultérieurement

La migration devra suivre :

```text
Backup
 ↓
Audit des données
 ↓
Création Organizations
 ↓
Mapping anciens utilisateurs → User
 ↓
Création OrganizationUser
 ↓
Attribution des données à organization_id
 ↓
Validation des FK
 ↓
Tests d'isolation
 ↓
Activation des contraintes NOT NULL
 ↓
RLS
```

**Aucune migration destructive sans sauvegarde et validation.**

---

## 22. Stratégie de création des Organizations

Lors de l'inscription d'une nouvelle entreprise :

```text
Signup
 ↓
Create User
 ↓
Create Organization
 ↓
Create OrganizationUser(owner)
 ↓
Create default Role(s)
 ↓
Assign permissions
 ↓
Create default settings
 ↓
Create Subscription / Trial
 ↓
Audit
```

Tout doit être réalisé dans une transaction lorsque cela est possible.

---

## 23. Rôles par défaut

Les rôles pourront être :

```text
OWNER
ADMIN
MANAGER
COMMERCIAL
CASHIER
STOCK_MANAGER
ACCOUNTANT
VIEWER
```

Les permissions doivent être configurables par organization, avec des restrictions éventuelles imposées par le plan SaaS.

---

## 24. Tenant-aware caching

Tout cache contenant des données métier doit inclure le tenant dans sa clé.

Mauvais :

```text
clients:list
```

Correct :

```text
org:123:clients:list
```

Pour un cache utilisateur :

```text
org:123:user:45:dashboard
```

Une invalidation doit également être tenant-aware.

---

## 25. Jobs asynchrones

Celery ou autre système de tâches doit transporter explicitement le contexte nécessaire :

```text
organization_id
user_id éventuel
job_id
```

Une tâche ne doit jamais utiliser une organization globale implicite.

Exemple : génération d'un rapport :

```text
ReportJob
 ├── organization_id
 ├── requested_by
 ├── filters
 └── format
```

---

## 26. Exports et rapports

Les exports sont un risque important de fuite de données.

Toute génération Excel/PDF/CSV doit :

1. charger le tenant courant ;
2. filtrer toutes les requêtes par `organization_id` ;
3. appliquer les permissions `reports.view` / `reports.export` ;
4. générer uniquement les données autorisées ;
5. journaliser l'export.

Un export ne doit jamais utiliser une requête globale comme :

```python
Sale.query.all()
```

---

## 27. BI / Analytics

Les dashboards doivent être tenant-aware jusque dans les requêtes SQL agrégées.

Correct :

```sql
SELECT SUM(total)
FROM sales
WHERE organization_id = :current_org_id;
```

Incorrect :

```sql
SELECT SUM(total)
FROM sales;
```

Les caches KPI doivent également être partitionnés par organization.

---

## 28. Billing SaaS

Le billing AFRIVA possède une particularité : il concerne l'organisation cliente mais est administré au niveau plateforme.

```text
AFRIVA Platform
      │
      ├── Plan
      ├── Subscription
      └── Invoice
             │
          Organization
```

Les administrateurs plateforme peuvent avoir un contexte système distinct, mais ce privilège doit être explicitement séparé des utilisateurs d'une organization cliente.

**Ne jamais donner aux utilisateurs tenant ordinaires un rôle de plateforme par défaut.**

---

## 29. Super Admin plateforme

Prévoir deux niveaux :

```text
TENANT USER
    ≠
PLATFORM ADMIN
```

Un Platform Admin peut avoir des permissions globales telles que :

```text
platform.organizations.view
platform.organizations.suspend
platform.billing.view
platform.audit.view
platform.users.manage
```

Ces permissions ne doivent pas être confondues avec les permissions métier d'une organization.

Toute impersonation éventuelle doit être :

- explicitement activée ;
- limitée dans le temps ;
- totalement auditée ;
- visuellement signalée.

---

## 30. Secrets et configuration

Les secrets restent hors Git :

```text
DATABASE_URL
SECRET_KEY
JWT_SECRET_KEY
REDIS_URL
SMTP credentials
Payment credentials
AWS credentials
Sentry DSN
```

Le `.env.example` ne contient que des placeholders.

---

## 31. Evolution future : Schema-per-Tenant

Le choix initial est :

```text
Shared Database
Shared Schema
organization_id
```

Une évolution future vers :

```text
Shared Database
Schema-per-Tenant
```

reste possible si AFRIVA atteint un volume ou des contraintes réglementaires justifiant cette complexité.

### Condition de migration

Cette évolution sera facilitée si toutes les couches applicatives utilisent déjà le tenant context :

```text
Route
 ↓
Service
 ↓
Repository
 ↓
Tenant
```

Le code métier ne doit donc pas dépendre directement de détails physiques du schéma PostgreSQL.

---

## 32. Definition of Done — Phase 2

La Phase 2 est considérée comme validée lorsque :

- [x] modèle Shared Database / Shared Schema défini ;
- [x] classification des données définie ;
- [x] modèle User / OrganizationUser / Organization défini ;
- [x] tenant context défini ;
- [x] RBAC défini ;
- [x] repository tenant-aware défini ;
- [x] service tenant-aware défini ;
- [x] audit trail défini ;
- [x] soft delete défini ;
- [x] règles cross-tenant définies ;
- [x] POS et stock traités comme domaines sensibles ;
- [x] stratégie RLS définie ;
- [x] stratégie de migration définie ;
- [x] tests de sécurité définis ;
- [x] stratégie cache/jobs/exports/BI définie.

---

## 33. Passage à la Phase 3

Le prochain chantier est le **socle applicatif multi-tenant**.

### Fichiers à créer

```text
app/__init__.py
app/models/base.py
app/models/organization.py
app/models/user.py
app/models/role.py
app/models/activity_log.py

app/middleware/tenant_middleware.py
app/middleware/auth_middleware.py

app/repositories/base_repository.py
app/services/base_service.py

app/permissions/decorators.py

migrations/versions/001_*.py

tests/conftest.py
tests/fixtures/*.py
tests/test_tenant_isolation.py
tests/security/test_rbac.py
```

### Ordre d'implémentation

```text
1. Flask Application Factory
2. Configuration / environnement
3. SQLAlchemy
4. Alembic
5. Organization
6. User
7. OrganizationUser
8. Role
9. Permission
10. ActivityLog
11. Authentication
12. Tenant Context
13. RBAC
14. Repository
15. Service
16. Tests
17. CI
```

### Gate de sécurité

**Aucun module CRM, POS ou Stock ne doit être développé avant que les tests d'isolation multi-tenant du socle soient verts.**

---

## 34. Décision finale

AFRIVA adopte officiellement le modèle :

> **Shared Database / Shared Schema + Tenant Context serveur + `organization_id` obligatoire + RBAC + Repository/Service tenant-aware + Audit Trail + tests cross-tenant + PostgreSQL RLS en défense en profondeur.**

La règle la plus importante reste :

> **Le tenant courant est une propriété de sécurité du serveur, pas une donnée de confiance fournie par le client.**

Toute future fonctionnalité AFRIVA doit respecter ce document avant d'être fusionnée dans `main`.

---

**Statut : PHASE 2 VALIDÉE**  
**Prochaine étape : PHASE 3 — SOCLE MULTI-TENANT**
