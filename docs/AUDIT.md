# Audit technique complet — AFRIVA SaaS

**Date :** 28 août 2026  
**Branche auditée :** `main`  
**Repository :** `Nasora-group/AFRIVA`  
**Type cible :** SaaS B2B multi-tenant, Shared Database / Shared Schema  
**Stack cible :** Flask / SQLAlchemy / PostgreSQL / HTML-CSS-JavaScript / REST JSON

---

## 1. Résumé exécutif

### Verdict

**AFRIVA est actuellement une ossature documentaire et non encore une application SaaS fonctionnelle.**

L'audit du contenu réellement présent sur la branche `main` montre un repository très léger : documentation d'architecture, plan de développement, structure projet, guide de démarrage et `requirements.txt`. L'arborescence récursive auditée ne contient actuellement ni `app/`, ni modèles SQLAlchemy, ni routes Flask, ni migrations Alembic, ni tests, ni templates, ni configuration applicative. Le fichier `00_START_HERE.md` confirme lui-même que plusieurs éléments de structure et de configuration doivent encore être créés.

Cette situation est saine pour une reconstruction propre : **il ne faut pas essayer de transformer progressivement un ancien code sans architecture**, mais établir d'abord le socle sécurisé puis construire les modules métier autour d'un tenant context centralisé.

### Niveau de maturité estimé

| Domaine | État | Risque |
|---|---|---|
| Documentation produit | 🟢 Bonne base | Faible |
| Architecture cible | 🟢 Définie | Moyen |
| Code applicatif | 🔴 Absent | Critique |
| Base de données | 🔴 Non implémentée | Critique |
| Multi-tenant réel | 🔴 Non implémenté | Critique |
| Authentification | 🔴 Non implémentée | Critique |
| RBAC | 🔴 Non implémenté | Critique |
| Audit trail | 🔴 Non implémenté | Élevé |
| CRM | 🔴 Non implémenté | Élevé |
| Ventes terrain | 🔴 Non implémenté | Élevé |
| POS / caisse | 🔴 Non implémenté | Critique |
| Stock | 🔴 Non implémenté | Critique |
| Billing SaaS | 🔴 Non implémenté | Élevé |
| BI / rapports | 🔴 Non implémenté | Moyen |
| Tests | 🔴 Non implémentés | Critique |
| CI/CD | 🔴 Non présent dans l'arborescence | Élevé |
| Déploiement | 🔴 Non implémenté | Élevé |

---

## 2. Périmètre réellement trouvé dans le repository

La branche `main` contient actuellement les éléments suivants :

```text
00_START_HERE.md
ARCHITECTURE.md
DEVELOPMENT_PLAN.md
PROJECT_STRUCTURE.md
QUICK_START.md
README.md
requirements.txt
```

L'arborescence récursive Git auditée ne fait apparaître aucun répertoire applicatif ou de tests. Cette observation est importante : les répertoires décrits dans la documentation (`app/`, `migrations/`, `tests/`, `config/`, `scripts/`, `docker/`, `.github/`) sont actuellement des éléments d'architecture cible, pas des composants déjà implémentés. fileciteturn0file0

Le document de démarrage indique également explicitement que `.gitignore`, `setup.py` et `pytest.ini` doivent encore être créés et fournit des commandes `mkdir` destinées à générer la structure. fileciteturn4file0

### Conséquence

Toutes les affirmations de la documentation concernant des fonctionnalités comme MFA, POS, stock, API, facturation ou BI doivent être considérées comme **spécifications fonctionnelles**, et non comme fonctionnalités disponibles aujourd'hui.

---

## 3. Analyse de l'architecture actuelle

La documentation définit une architecture en couches cohérente :

```text
Présentation
    ↓
API REST
    ↓
Services métier
    ↓
Middleware sécurité / tenant / permissions
    ↓
Repositories tenant-aware
    ↓
SQLAlchemy / PostgreSQL
```

Cette direction est pertinente pour AFRIVA, notamment parce qu'elle permet de concentrer les règles de sécurité dans des composants réutilisables plutôt que de les recopier dans chaque route. L'architecture cible prévoit notamment `TenantMiddleware`, `AuthMiddleware`, `PermissionMiddleware` et des repositories tenant-aware. fileciteturn2file0

### Recommandation architecturale

Conserver cette architecture mais renforcer une règle : **aucune route métier ne doit pouvoir décider elle-même quel `organization_id` elle peut lire ou écrire.** Le tenant courant doit provenir du contexte serveur authentifié et être contrôlé par middleware/service/repository.

Le client HTTP ne doit jamais être considéré comme une source de vérité pour l'identité du tenant.

---

## 4. Analyse du multi-tenant

### État actuel

Le multi-tenant est **documenté mais non implémenté**.

Le README fixe correctement l'objectif : Shared Database / Shared Schema avec isolation absolue entre organizations. fileciteturn1file0

### Architecture recommandée

```text
User
 └── OrganizationUser
       ├── Organization
       └── Role

Request
  ↓
Authentication
  ↓
Tenant Context
  ↓
Permission Check
  ↓
Service
  ↓
Tenant-aware Repository
  ↓
SQLAlchemy
  ↓
PostgreSQL
```

### Règle absolue

Pour toute entité appartenant à une entreprise :

```python
organization_id = db.Column(
    db.Integer,
    db.ForeignKey("organization.id"),
    nullable=False,
    index=True,
)
```

Les requêtes doivent toujours être bornées par le tenant courant :

```python
Model.query.filter_by(
    organization_id=current_org.id,
    id=resource_id,
).first()
```

Il faut éviter toute API de type :

```text
GET /organizations/<organization_id>/clients
```

comme mécanisme de confiance. Un utilisateur pourrait tenter de remplacer l'identifiant. Le serveur doit vérifier l'appartenance à l'organisation puis utiliser `g.current_org_id`.

### Renforcement recommandé : PostgreSQL Row Level Security

Pour AFRIVA, la protection applicative doit être complétée à moyen terme par PostgreSQL RLS sur les tables sensibles. Le repository/service reste obligatoire, mais RLS fournit une seconde barrière contre une erreur de code.

---

## 5. Modèle User / Organization

La documentation propose correctement de séparer l'identité globale du rattachement à une entreprise :

```text
User
  ↓
OrganizationUser
  ↓
Organization + Role
```

Cette conception permet à un même utilisateur d'appartenir à plusieurs organizations. fileciteturn2file0

### Recommandations

Ajouter/garantir :

- contrainte unique `(user_id, organization_id)` ;
- statut de l'affiliation (`active`, `invited`, `suspended`, etc.) ;
- `current_org_id` uniquement dans la session/contexte, jamais comme autorité indépendante ;
- journalisation des changements d'organisation ;
- expiration des sessions sensibles ;
- invalidation de session après changement de mot de passe ou suspension ;
- index sur `organization_id`, `user_id` et les combinaisons fréquemment utilisées.

---

## 6. Authentification et sécurité

### État

Aucun code d'authentification n'est actuellement présent dans le repository audité.

La documentation prévoit Flask-Login, JWT, bcrypt, MFA/TOTP et sessions sécurisées. fileciteturn3file0

### Recommandation

Pour l'application web classique :

- Flask-Login / session serveur comme mécanisme principal ;
- cookies `HttpOnly`, `Secure`, `SameSite=Lax` ou `Strict` selon les flux ;
- CSRF pour les formulaires et mutations browser ;
- bcrypt/Argon2 pour les mots de passe ;
- limitation des tentatives de connexion ;
- réinitialisation de mot de passe avec jeton à durée limitée ;
- MFA obligatoire pour les comptes administrateurs sensibles ;
- JWT uniquement pour les cas d'API où il est réellement nécessaire.

**Ne pas activer simultanément plusieurs mécanismes d'authentification sans politique claire.** Cela augmenterait la surface d'attaque.

---

## 7. RBAC / Permissions

### État

Le RBAC est spécifié mais non implémenté.

### Architecture recommandée

```text
User
  ↓
OrganizationUser
  ↓
Role
  ↓
RolePermission
  ↓
Permission
```

Les permissions doivent être indépendantes du tenant et les rôles peuvent être globaux ou spécifiques à une organization selon le besoin.

Permissions minimales à prévoir :

```text
clients.view
clients.create
clients.update
clients.delete

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

### Point critique

`@require_permission()` doit être combiné au tenant context. Une permission seule ne prouve jamais qu'une ressource appartient à l'organisation courante.

---

## 8. Audit Trail

### État

Le journal d'activité est prévu dans l'architecture mais non implémenté.

### À implémenter avant les modules financiers

Créer `ActivityLog` avec au minimum :

- `organization_id`
- `user_id`
- `action`
- `resource_type`
- `resource_id`
- `ip_address`
- `user_agent`
- `metadata` JSONB
- `created_at`

Actions obligatoirement journalisées :

- connexion/déconnexion ;
- changement de tenant ;
- création/modification/annulation de vente ;
- remise POS ;
- ouverture/clôture de caisse ;
- entrée/sortie de caisse ;
- ajustement de stock ;
- transfert de stock ;
- modification des permissions ;
- création/suspension d'utilisateur ;
- facturation et changements d'abonnement.

---

## 9. Suppression des données

La règle fonctionnelle est correcte : **pas de suppression physique pour les données métier sensibles**.

À appliquer particulièrement à :

- ventes ;
- paiements ;
- sessions de caisse ;
- mouvements de stock ;
- factures ;
- logs d'activité.

Pour les entités appropriées, prévoir :

```text
deleted_at
is_deleted
```

ou un statut métier explicite lorsque celui-ci représente mieux le cycle de vie.

Attention : une annulation de vente ne doit pas simplement changer un statut. Elle doit également déclencher les écritures métier nécessaires (stock, caisse, audit, éventuellement remboursement) dans une transaction cohérente.

---

## 10. Analyse de la base de données

### État

Aucune migration ou modèle SQLAlchemy n'est présent dans l'arborescence auditée. Il n'existe donc pas encore de schéma PostgreSQL réel à auditer.

### Schéma cible minimal

```text
organization
user
organization_user
role
permission
role_permission
activity_log

store
cash_register
cash_session

product
product_stock
stock_movement
product_batch
stock_transfer
inventory

client
prospect
contact
commercial
visit
prospection
tour

sales_sale
sales_sale_item
objective
performance

pos_sale
pos_sale_item
payment
receipt
cash_in
cash_out

plan
subscription
invoice
billing_payment
```

### Recommandations PostgreSQL

- `NUMERIC(18,2)` pour les montants financiers, jamais `Float` ;
- `TIMESTAMP WITH TIME ZONE` pour les événements ;
- `JSONB` pour les métadonnées/audit flexibles ;
- indexes composites commençant par `organization_id` sur les tables fortement interrogées ;
- contraintes FK strictes ;
- contraintes `CHECK` pour les statuts et montants lorsque possible ;
- transactions ACID pour vente + paiement + stock + caisse ;
- éviter les cascades destructrices sur les données financières.

---

## 11. POS / Caisse enregistreuse

### État

Le POS est uniquement spécifié dans la documentation.

La hiérarchie prévue est pertinente :

```text
Organization
  ↓
Store
  ↓
CashRegister
  ↓
CashSession
  ↓
POS Sale
  ↓
Payment
  ↓
Receipt
```

Le workflow documenté prévoit ouverture, vente, paiement, ticket, mise à jour du stock puis clôture. fileciteturn2file0

### Point architectural critique

**Ne pas mélanger la vente terrain et la vente POS dans une même table sans distinction métier claire.**

Une vente commerciale peut représenter une commande ou une vente réalisée par un commercial, tandis qu'une vente POS est une transaction de caisse. Les deux peuvent partager des concepts (`Product`, `Customer`, `Payment`) mais doivent conserver leurs cycles de vie distincts.

### Caisse

Une session de caisse doit enregistrer :

- utilisateur ;
- caisse ;
- magasin ;
- montant d'ouverture ;
- entrées ;
- sorties ;
- ventes par mode de paiement ;
- montant théorique ;
- montant réellement compté ;
- écart ;
- date/heure d'ouverture ;
- date/heure de clôture ;
- validation.

---

## 12. Stock et pharmacie

Le périmètre stock est adapté aux entreprises visées : multi-magasins, transferts, inventaires, lots et expiration. fileciteturn1file0

### Recommandations critiques

Pour les pharmacies :

- numéro de lot ;
- date d'expiration ;
- prix d'achat ;
- prix de vente ;
- quantité ;
- emplacement ;
- fournisseur ;
- traçabilité des mouvements ;
- stratégie FEFO (First Expired, First Out) pour les produits concernés ;
- blocage ou alerte des lots expirés ;
- gestion des produits nécessitant une traçabilité renforcée.

Toute modification de stock doit être atomique et auditée.

---

## 13. CRM et force de vente

Le périmètre CRM prévu comprend clients, prospects, contacts, commerciaux, visites, prospections et tournées. fileciteturn2file0

Chaque entité métier devra porter ou hériter de `organization_id` lorsqu'elle est tenant-owned.

### Attention aux relations indirectes

Un simple filtre sur `commercial_id` ne suffit pas si le commercial appartient à une autre organization. Toutes les relations doivent être validées dans le tenant courant.

Exemple : lors de la création d'une visite, vérifier simultanément :

```text
visit.organization_id == current_org.id
commercial.organization_id == current_org.id
client.organization_id == current_org.id
```

---

## 14. Facturation SaaS

Le billing concerne AFRIVA lui-même en tant que plateforme SaaS. Il faut donc distinguer :

1. **Facturation SaaS de l'organization** : abonnement AFRIVA ;
2. **Ventes de l'entreprise cliente** : ventes POS/terrain de son activité.

Ces deux domaines ne doivent jamais partager la même sémantique financière.

### Plans

Les plans documentés sont :

```text
FREE
STARTER
BUSINESS
PROFESSIONAL
ENTERPRISE
```

Les limites devront être configurables :

- nombre d'utilisateurs ;
- magasins ;
- caisses ;
- produits ;
- volume de transactions ;
- stockage ;
- modules activés ;
- exports/API ;
- support.

---

## 15. API REST

### État

Les endpoints sont documentés mais aucune route API n'est actuellement implémentée.

### Règles obligatoires

Chaque endpoint doit respecter :

```text
Authentication
→ Tenant Context
→ Permission
→ Validation input
→ Service
→ Repository tenant-aware
→ Audit
→ Response
```

Ne jamais faire confiance à un `organization_id` fourni dans le JSON pour déterminer le tenant cible.

Pour les ressources par ID :

```python
resource = repository.get_for_organization(
    current_org.id,
    resource_id,
)
```

Si la ressource appartient à un autre tenant, elle doit se comporter comme inexistante ou retourner une réponse contrôlée sans fuite d'information.

---

## 16. Dépendances Python

Le `requirements.txt` contient une base technologique cohérente pour le projet : Flask, SQLAlchemy, PostgreSQL, Flask-Login, JWT, bcrypt, Redis, Celery, pyotp, outils de reporting, pytest et outils de qualité. fileciteturn3file0

### Points à corriger avant production

1. **Dépendances anciennes** : les versions sont datées et devront être réévaluées avant implémentation finale.
2. **Doublon `flask-restx`** : il apparaît deux fois.
3. **Surface de dépendances importante** : Stripe, PayPal, Twilio, boto3, Celery, New Relic, Sentry, etc. ne doivent être ajoutés à l'exécution que lorsqu'ils sont réellement utilisés.
4. **Compatibilité Python** : fixer une version Python supportée et la tester en CI.
5. **Locking** : produire un lock reproductible pour éviter les dérives de dépendances.
6. **Sécurité supply-chain** : scanner les dépendances et mettre en place une politique de mise à jour.

---

## 17. Configuration et secrets

Le repository doit impérativement contenir un `.env.example` sans secrets réels, puis utiliser des variables d'environnement pour :

```text
DATABASE_URL
SECRET_KEY
JWT_SECRET_KEY
REDIS_URL
MAIL_* 
STRIPE_* 
PAYPAL_* 
TWILIO_* 
AWS_* 
SENTRY_DSN
```

Aucun secret ne doit être commité.

Le `.gitignore` doit au minimum couvrir :

```text
.env
.env.*
!.env.example
venv/
.venv/
__pycache__/
.pytest_cache/
.coverage
htmlcov/
*.pyc
instance/
```

---

## 18. Tests

### État

Aucun test n'est présent actuellement.

### Priorité absolue

Créer une suite de tests de sécurité avant de développer massivement les modules métier.

### Tests obligatoires

#### Isolation

Pour chaque modèle tenant-aware :

```text
Org A crée X
Org B tente de lire X → refus / None
Org B tente de modifier X → refus
Org B tente de supprimer/annuler X → refus
Org B tente de référencer X dans une autre opération → refus
```

#### RBAC

Tester chaque permission critique avec :

- utilisateur autorisé ;
- utilisateur non autorisé ;
- utilisateur d'une autre organization.

#### POS

Tester :

- impossibilité de vendre avec une caisse d'un autre tenant ;
- impossibilité de clôturer la caisse d'un autre tenant ;
- paiement total/partiel/mixte ;
- remise selon permission ;
- transaction atomique stock + caisse + vente.

#### Stock

Tester :

- transfert inter-tenant interdit ;
- stock négatif selon politique ;
- lot expiré ;
- inventaire ;
- concurrence sur quantité.

### Objectif

Minimum **80 % de couverture globale**, avec une couverture nettement supérieure sur les composants sécurité, tenant context, repositories, services financiers et stock.

---

## 19. CI/CD

L'arborescence auditée ne contient actuellement pas de workflow GitHub Actions. La CI doit être créée avant le premier gros développement.

Pipeline minimal :

```text
push / pull_request
    ↓
Install dependencies
    ↓
Lint (flake8/black/isort)
    ↓
Unit tests
    ↓
Integration tests
    ↓
Security tests
    ↓
Coverage threshold
    ↓
Build
```

### Règle de branche

```text
main       = production
 develop   = intégration
 feature/* = développement
 fix/*     = correction
```

Aucun merge vers `main` sans tests passants et revue.

---

## 20. Stratégie de migration

Puisqu'il n'existe actuellement pas de schéma applicatif dans le repository, **la migration vers le multi-tenant doit être conçue comme une fondation initiale et non comme une migration destructive.**

### Ordre recommandé

#### Étape 1 — Socle

Créer :

```text
Organization
User
OrganizationUser
Role
Permission
RolePermission
ActivityLog
```

#### Étape 2 — Tenant context

Créer :

```text
get_current_organization()
load_tenant_context()
require_permission()
```

#### Étape 3 — Repositories

Créer un `BaseRepository` qui impose explicitement le tenant.

#### Étape 4 — Services

Créer un `BaseService` qui ne récupère le tenant que depuis le contexte serveur.

#### Étape 5 — Tests sécurité

Faire passer les tests cross-tenant avant de commencer le CRM.

#### Étape 6 — Modules métier

Ordre recommandé :

```text
CRM
→ Produits
→ Ventes terrain
→ POS
→ Stock avancé
→ Billing
→ Reports
→ BI
```

Le POS et le stock doivent être développés avec des transactions et tests d'intégration solides.

---

## 21. Risques majeurs

### 🔴 R1 — Fausse impression de fonctionnalité

La documentation décrit une plateforme complète alors que le code n'est pas encore présent.

**Action :** considérer `main` comme une spécification initiale, pas comme une application opérationnelle.

### 🔴 R2 — Fuite cross-tenant

C'est le risque numéro 1 d'AFRIVA.

**Action :** tenant context centralisé + repositories obligatoires + tests systématiques + RLS ultérieur.

### 🔴 R3 — Mélange POS / ventes terrain

Peut provoquer des incohérences de caisse, stock et reporting.

**Action :** séparer les cycles métier tout en partageant les référentiels.

### 🔴 R4 — Incohérences financières

Une vente peut toucher plusieurs domaines : stock, caisse, paiement, ticket, audit.

**Action :** transaction DB unique pour chaque opération atomique.

### 🔴 R5 — RBAC incomplet

Une route protégée par login mais non par permission peut exposer une fonction administrative.

**Action :** permission explicite pour chaque mutation et fonction sensible.

### 🟠 R6 — Dépendances vieillissantes

**Action :** audit et mise à niveau avant production.

### 🟠 R7 — Absence de CI

**Action :** mettre GitHub Actions en place dès la Phase 3.

### 🟠 R8 — Absence de migrations réelles

**Action :** Alembic comme source de vérité du schéma.

---

## 22. Architecture cible validée

```text
                    AFRIVA SaaS
                         │
             ┌───────────▼───────────┐
             │ Authenticated Request │
             └───────────┬───────────┘
                         │
             ┌───────────▼───────────┐
             │   Tenant Middleware   │
             │ current organization  │
             └───────────┬───────────┘
                         │
             ┌───────────▼───────────┐
             │ Permission / RBAC     │
             └───────────┬───────────┘
                         │
             ┌───────────▼───────────┐
             │     Service Layer     │
             │ business transactions│
             └───────────┬───────────┘
                         │
             ┌───────────▼───────────┐
             │ Tenant-aware          │
             │ Repository Layer      │
             └───────────┬───────────┘
                         │
             ┌───────────▼───────────┐
             │ SQLAlchemy / PostgreSQL│
             │ organization_id + RLS │
             └───────────────────────┘
```

---

## 23. Plan d'action immédiat

### Phase 1 — Audit

- [x] Examiner l'arborescence réelle
- [x] Examiner README
- [x] Examiner architecture
- [x] Examiner dépendances
- [x] Identifier l'écart entre documentation et code
- [x] Créer `docs/AUDIT.md`

### Phase 2 — Architecture multi-tenant

À réaliser ensuite :

- [ ] `docs/MULTI_TENANCY_PLAN.md`
- [ ] Définition finale du modèle tenant
- [ ] Matrice des entités tenant-aware / globales
- [ ] Politique de tenant context
- [ ] Politique RBAC
- [ ] Politique d'audit
- [ ] Stratégie RLS PostgreSQL

### Phase 3 — Socle

- [ ] `app/__init__.py`
- [ ] `app/models/base.py`
- [ ] Organization
- [ ] User
- [ ] OrganizationUser
- [ ] Role
- [ ] Permission
- [ ] ActivityLog
- [ ] Tenant middleware
- [ ] Auth middleware
- [ ] Permission decorator
- [ ] BaseRepository
- [ ] BaseService
- [ ] Alembic
- [ ] Tests d'isolation
- [ ] CI GitHub Actions

---

## 24. Critères de validation avant CRM

**Ne pas commencer le CRM tant que tous les critères suivants ne sont pas satisfaits :**

- [ ] Un utilisateur peut être rattaché à une ou plusieurs organizations.
- [ ] Une requête possède un tenant courant vérifié côté serveur.
- [ ] Une organization ne peut jamais sélectionner une autre organization arbitrairement.
- [ ] Les repositories filtrent obligatoirement par tenant.
- [ ] Les permissions sont vérifiées côté serveur.
- [ ] Les actions critiques sont journalisées.
- [ ] Les tests cross-tenant sont verts.
- [ ] Les migrations sont reproductibles.
- [ ] Aucun secret n'est présent dans Git.
- [ ] La CI bloque les régressions de sécurité.

---

## 25. Conclusion

**AFRIVA possède une bonne spécification architecturale, mais son implémentation doit encore être construite.** Le principal avantage est qu'il n'existe actuellement pas de dette applicative importante à préserver dans `main` : nous pouvons donc établir dès le départ une architecture multi-tenant stricte.

La priorité n'est pas de coder immédiatement le CRM ou le POS. La priorité est de construire un **socle de sécurité irréprochable** : `Organization → User/OrganizationUser → Tenant Context → RBAC → Repository tenant-aware → Service → Audit → Tests`.

Une fois ce socle validé, les modules CRM, ventes, POS, stock, facturation et BI pourront être ajoutés sans remettre en cause l'isolation des données.

### Décision d'architecture

> **AFRIVA doit être construit autour du tenant courant, jamais autour d'un `organization_id` fourni par le client.**

> **Toute nouvelle fonctionnalité doit être conçue tenant-aware dès sa première ligne de code.**

> **Aucune fonctionnalité financière (POS, paiement, stock, facturation) ne doit être considérée comme prête sans tests d'intégrité et tests cross-tenant.**

---

**Statut de l'audit : COMPLET — Phase 1**  
**Prochaine étape recommandée : Phase 2 — `MULTI_TENANCY_PLAN.md`**
