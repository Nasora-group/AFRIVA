# Architecture Technique - AFRIVA SaaS

## 🏗️ Vue d'ensemble de l'Architecture

AFRIVA est construit sur une architecture **multi-couches** et **multi-tenant** :

```
┌─────────────────────────────────────────────┐
│         Couche Présentation                 │
│     (HTML/CSS/JS/Bootstrap/Chart.js)        │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│         Couche API REST                     │
│      (/api/v1/clients, /api/v1/sales)      │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│    Couche Application (Services/Logic)      │
│   - AuthService                             │
│   - ClientService                           │
│   - SalesService                            │
│   - POSService                              │
│   - InventoryService                        │
│   - BillingService                          │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│   Couche Middleware & Sécurité              │
│   - TenantMiddleware                        │
│   - AuthMiddleware                          │
│   - PermissionMiddleware                    │
│   - RateLimitMiddleware                     │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│      Couche Persistance (Data Access)       │
│   - Repositories (tenant-aware)             │
│   - SQLAlchemy Models                       │
│   - Database Operations                     │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│         Base de Données PostgreSQL          │
│  (Shared Database / Shared Schema Model)    │
└─────────────────────────────────────────────┘
```

---

## 📦 Modules Principaux

### 1. **auth/** - Authentification & Autorisation
Gère la connexion, inscription, sessions et permissions.

**Fichiers clés:**
```
auth/
├── __init__.py
├── models.py           # User, Role, Permission
├── services.py         # AuthService
├── repositories.py     # UserRepository
├── routes.py           # /auth endpoints
├── decorators.py       # @login_required, @require_permission
└── utils.py            # Hash, JWT, etc.
```

**Fonctionnalités:**
- Inscription avec validation email
- Connexion avec session sécurisée
- Mot de passe oublié
- Changement de mot de passe
- MFA/TOTP pour Super Admin
- Gestion des API Keys (Enterprise)

### 2. **tenants/** - Gestion Multi-Tenant

Gère les organizations et l'isolation des données.

**Fichiers clés:**
```
tenants/
├── __init__.py
├── models.py           # Organization
├── services.py         # OrganizationService
├── repositories.py     # OrganizationRepository
├── routes.py           # /organizations endpoints
├── context.py          # TenantContext (CurrentOrganization)
└── middleware.py       # TenantMiddleware (identification du tenant)
```

**Fonctionnalités:**
- Création d'organisations
- Gestion des détails (logo, devise, timezone)
- Invitation d'utilisateurs
- Gestion des rôles par organization
- Tenant context dans chaque requête

### 3. **users/** - Gestion des Utilisateurs

Gère les utilisateurs et leurs affiliations aux organizations.

**Fichiers clés:**
```
users/
├── __init__.py
├── models.py           # User, OrganizationUser
├── services.py         # UserService
├── repositories.py     # UserRepository (tenant-aware)
├── routes.py           # /users endpoints
└── forms.py            # Validation des formulaires
```

**Modèles:**
```python
# Un utilisateur peut appartenir à plusieurs organizations
User
  ├── id
  ├── email
  ├── password_hash
  ├── first_name
  ├── last_name
  ├── status (active, inactive, suspended)
  └── organization_users (relation)
      └── OrganizationUser
          ├── user_id
          ├── organization_id
          ├── role_id
          └── created_at
```

### 4. **organizations/** - Gestion des Organizations

Détails et configuration des entreprises clients.

**Fichiers clés:**
```
organizations/
├── __init__.py
├── models.py           # Organization
├── services.py         # OrganizationService
├── repositories.py     # OrganizationRepository
├── routes.py           # /organizations endpoints
└── forms.py
```

**Modèles:**
```python
Organization
  ├── id
  ├── name
  ├── slug
  ├── logo
  ├── email
  ├── phone
  ├── address
  ├── city
  ├── country
  ├── currency (XOF, EUR, USD)
  ├── timezone
  ├── industry (pharmacy, retail, etc.)
  ├── status (trial, active, suspended, expired)
  ├── plan_id
  └── created_at
```

### 5. **crm/** - Gestion CRM

Clients, prospects, contacts, visites, prospections.

**Fichiers clés:**
```
crm/
├── __init__.py
├── models.py           # Client, Prospect, Contact, Visit, Prospection
├── services.py         # ClientService, VisitService, etc.
├── repositories.py     # ClientRepository (tenant-aware)
├── routes.py           # /clients, /prospects, /visits
└── forms.py
```

**Modèles principaux:**
- `Client` - Entreprise cliente
- `Prospect` - Prospect
- `Contact` - Personne de contact
- `Commercial` - Vendeur/représentant
- `Visit` - Visite client
- `Prospection` - Action de prospection
- `Tour` - Tournée commercial

### 6. **sales/** - Ventes Commerciales

Gestion des ventes terrain et objectifs.

**Fichiers clés:**
```
sales/
├── __init__.py
├── models.py           # Sale, SaleItem, Objective, Performance
├── services.py         # SalesService
├── repositories.py     # SalesRepository
├── routes.py           # /sales endpoints
└── forms.py
```

**Modèles:**
- `Sale` - Vente commerciale
- `SaleItem` - Ligne de vente
- `Objective` - Objectif de vente
- `Performance` - Performance commerciale

### 7. **pos/** - Module POS (Caisse)

Point of Sale, paiements, tickets, clôtures.

**Fichiers clés:**
```
pos/
├── __init__.py
├── models.py           # Store, CashRegister, CashSession, Payment, Receipt
├── services.py         # POSService, CashService, PaymentService
├── repositories.py     # POSRepository (tenant-aware)
├── routes.py           # /pos endpoints
├── forms.py
└── tickets.py          # Génération de tickets
```

**Modèles:**
```python
# Hiérarchie POS
Organization
  └── Store (magasin)
      └── CashRegister (caisse)
          └── CashSession (session)
              └── Sale (vente)
                  └── Payment (paiement)
                      └── Receipt (ticket)
```

**Workflow POS:**
```
Ouverture Caisse
  ↓
Vente (scanner, panier, remise)
  ↓
Paiement (espèces, carte, mobile money, mixte)
  ↓
Ticket (thermique, PDF, email)
  ↓
Mise à jour Stock
  ↓
Clôture Caisse (compter, valider, écarts)
```

### 8. **inventory/** - Gestion des Stocks

Produits, stocks, mouvements, inventaires, transferts.

**Fichiers clés:**
```
inventory/
├── __init__.py
├── models.py           # Product, ProductStock, StockMovement, Inventory, ProductBatch
├── services.py         # InventoryService
├── repositories.py     # InventoryRepository
├── routes.py           # /inventory endpoints
└── forms.py
```

**Modèles:**
- `Product` - Produit
- `ProductStock` - Stock par magasin
- `StockMovement` - Mouvement de stock
- `Inventory` - Inventaire
- `ProductBatch` - Lot (pharmacie)
- `StockTransfer` - Transfert entre magasins

### 9. **billing/** - Facturation SaaS

Plans, abonnements, facturation, paiements.

**Fichiers clés:**
```
billing/
├── __init__.py
├── models.py           # Plan, Subscription, Invoice, Payment
├── services.py         # BillingService, SubscriptionService
├── repositories.py     # BillingRepository
├── routes.py           # /billing endpoints
├── providers/          # Stripe, PayPal, etc.
│   ├── stripe.py
│   ├── paypal.py
│   └── base.py
└── forms.py
```

**Modèles:**
- `Plan` - Plan d'abonnement (FREE, STARTER, BUSINESS, PROFESSIONAL, ENTERPRISE)
- `Subscription` - Abonnement d'une organization
- `Invoice` - Facture
- `Payment` - Paiement de facture

### 10. **reports/** - Rapports & Exports

Génération de rapports, exports Excel/PDF.

**Fichiers clés:**
```
reports/
├── __init__.py
├── models.py           # Report
├── services.py         # ReportService
├── generators/         # Générateurs de rapports
│   ├── sales_report.py
│   ├── pos_report.py
│   ├── stock_report.py
│   └── client_report.py
├── exporters/          # Exporteurs (Excel, PDF, CSV)
│   ├── excel_exporter.py
│   ├── pdf_exporter.py
│   └── csv_exporter.py
└── routes.py           # /reports endpoints
```

### 11. **analytics/** - Business Intelligence

Dashboards, KPI, visualisations.

**Fichiers clés:**
```
analytics/
├── __init__.py
├── services.py         # AnalyticsService
├── dashboards.py       # Dashboard definitions
├── queries.py          # Requêtes optimisées pour BI
└── routes.py           # /analytics endpoints
```

**Dashboards:**
- Dashboard Enterprise (CA, objectifs, clients, stocks)
- Dashboard POS (CA, tickets, panier moyen, caisses)
- Dashboard Commercial (visites, prospections, performances)
- Dashboard Stock (ruptures, transferts, inventaires)

### 12. **api/** - Routes API

Endpoints RESTful pour l'intégration.

**Structure:**
```
api/
├── __init__.py
├── v1/                 # Version 1 de l'API
│   ├── __init__.py
│   ├── auth.py
│   ├── organizations.py
│   ├── users.py
│   ├── clients.py
│   ├── prospects.py
│   ├── products.py
│   ├── sales.py
│   ├── pos.py
│   ├── payments.py
│   ├── inventory.py
│   ├── reports.py
│   └── webhooks.py
└── v2/                 # Version 2 (future)
```

**Endpoints principaux:**
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout

GET    /api/v1/organizations
POST   /api/v1/organizations
GET    /api/v1/organizations/{id}
PUT    /api/v1/organizations/{id}

GET    /api/v1/clients
POST   /api/v1/clients
GET    /api/v1/clients/{id}
PUT    /api/v1/clients/{id}

GET    /api/v1/products
POST   /api/v1/products
PUT    /api/v1/products/{id}

POST   /api/v1/pos/sales
POST   /api/v1/pos/payments
GET    /api/v1/pos/cash-register/{id}/report

GET    /api/v1/inventory/stocks
POST   /api/v1/inventory/stock-movements
POST   /api/v1/inventory/transfers

GET    /api/v1/reports
POST   /api/v1/reports/export

GET    /api/v1/analytics/dashboard
```

### 13. **models/** - Modèles de Données

Tous les modèles SQLAlchemy centralisés.

**Fichiers clés:**
```
models/
├── __init__.py
├── base.py             # Classe de base avec id, created_at, updated_at
├── user.py             # User, OrganizationUser
├── organization.py     # Organization
├── role.py             # Role, Permission
├── crm.py              # Client, Prospect, Contact, etc.
├── product.py          # Product, ProductCategory
├── sales.py            # Sale, SaleItem
├── pos.py              # Store, CashRegister, CashSession, Receipt
├── payment.py          # Payment, Refund
├── inventory.py        # ProductStock, StockMovement, Inventory
├── billing.py          # Plan, Subscription, Invoice
├── objective.py        # Objective, Performance
└── audit.py            # ActivityLog
```

### 14. **services/** - Logique Métier

Services spécialisés pour chaque domaine.

**Fichiers clés:**
```
services/
├── __init__.py
├── auth_service.py
├── tenant_service.py
├── user_service.py
├── organization_service.py
├── client_service.py
├── sales_service.py
├── pos_service.py
├── cash_service.py
├── payment_service.py
├── inventory_service.py
├── stock_service.py
├── billing_service.py
├── report_service.py
├── notification_service.py
└── base_service.py     # Service de base tenant-aware
```

**Exemple de service tenant-aware:**
```python
class BaseService:
    """Service de base avec tenant awareness"""
    
    def __init__(self, repository):
        self.repo = repository
    
    def get_for_current_org(self, id):
        current_org = get_current_organization()
        return self.repo.get_for_organization(current_org.id, id)
    
    def list_for_current_org(self, **filters):
        current_org = get_current_organization()
        return self.repo.list_for_organization(current_org.id, **filters)
```

### 15. **repositories/** - Accès aux Données

Repositories tenant-aware pour l'isolation des données.

**Fichiers clés:**
```
repositories/
├── __init__.py
├── base_repository.py  # BaseRepository tenant-aware
├── user_repository.py
├── organization_repository.py
├── client_repository.py
├── product_repository.py
├── sales_repository.py
├── pos_repository.py
└── inventory_repository.py
```

**Exemple tenant-aware:**
```python
class BaseRepository:
    """Repository de base avec tenant filtering"""
    
    def get_for_organization(self, org_id, id):
        return self.model.query.filter(
            self.model.organization_id == org_id,
            self.model.id == id
        ).first()
    
    def list_for_organization(self, org_id, **filters):
        query = self.model.query.filter(
            self.model.organization_id == org_id
        )
        # Appliquer les filtres
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()
```

### 16. **permissions/** - Gestion des Permissions (RBAC)

Système de rôles et permissions.

**Fichiers clés:**
```
permissions/
├── __init__.py
├── models.py           # Role, Permission, RolePermission
├── default_roles.py    # Rôles par défaut
├── decorators.py       # @require_permission("clients.view")
└── utils.py            # Fonctions de vérification
```

**Rôles par défaut:**
- Super Admin AFRIVA
- Organization Owner
- Administrator
- Director
- Sales Manager
- Commercial
- Cashier
- Stock Manager
- Accountant
- Viewer

**Permissions:**
```
clients.view
clients.create
clients.update
clients.delete

sales.view
sales.create
sales.update
sales.cancel
sales.refund

pos.open
pos.sell
pos.discount
pos.refund
pos.close

inventory.view
inventory.adjust
inventory.transfer

reports.view
reports.export
```

### 17. **middleware/** - Middlewares

Middlewares Flask pour les traitements transversaux.

**Fichiers clés:**
```
middleware/
├── __init__.py
├── tenant_middleware.py        # Identification et contexte du tenant
├── auth_middleware.py          # Authentification
├── permission_middleware.py    # Vérification des permissions
├── rate_limit_middleware.py    # Limitation de débit
├── security_middleware.py      # Headers de sécurité
├── tenant_context_middleware.py  # Contexte du tenant dans g
└── cors_middleware.py          # CORS
```

**TenantMiddleware:**
```python
def tenant_middleware():
    """Identifie et charge le tenant courant"""
    user = get_current_user()
    org_id = request.args.get('org_id') or session.get('org_id')
    
    if not org_id and user:
        # Utiliser la première organization de l'utilisateur
        org = user.organization_users[0].organization
        org_id = org.id
    
    set_current_organization(org_id)
    g.current_organization = get_organization(org_id)
```

### 18. **utils/** - Utilitaires

Fonctions utilitaires communes.

**Fichiers clés:**
```
utils/
├── __init__.py
├── decorators.py       # Décorateurs customisés
├── validators.py       # Validateurs métier
├── formatters.py       # Formatage (devise, date, etc.)
├── file_handlers.py    # Gestion des fichiers
├── email_sender.py     # Envoi d'emails
├── sms_sender.py       # Envoi de SMS
└── cache.py            # Gestion du cache tenant-aware
```

---

## 🔗 Flux de Requête

### Exemple : Récupérer les clients de l'utilisateur

```
1. Requête: GET /api/v1/clients
   Headers: { "Authorization": "Bearer token" }

2. TenantMiddleware
   - Vérifie le token
   - Identifie l'utilisateur
   - Charge l'organization
   - Stocke le contexte dans g.current_organization

3. AuthMiddleware
   - Vérifie que l'utilisateur est connecté

4. PermissionMiddleware
   - Vérifie que l'utilisateur a "clients.view"

5. Route Handler (ClientRoute)
   def get_clients():
       current_org = get_current_organization()
       return ClientService.list_for_org(current_org.id)

6. ClientService.list_for_org()
   org_id = current_org.id
   clients = ClientRepository.list_for_organization(org_id)

7. ClientRepository.list_for_organization()
   query = Client.query.filter(Client.organization_id == org_id)
   return query.all()

8. Response: JSON avec les clients de l'organization
```

---

## 💾 Modèle de Base de Données

### Schéma Multi-Tenant (Shared Database / Shared Schema)

Toutes les tables ont un `organization_id` :

```sql
CREATE TABLE organization (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    currency VARCHAR(3) DEFAULT 'XOF',
    timezone VARCHAR(50) DEFAULT 'Africa/Dakar',
    status VARCHAR(50) DEFAULT 'trial',
    plan_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE organization_user (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id),
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    role_id INTEGER NOT NULL REFERENCES role(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, organization_id)
);

CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    commercial_id INTEGER REFERENCES commercial(id),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    sku VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    purchase_price DECIMAL(10,2),
    sale_price DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, sku)
);

CREATE TABLE sale (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    commercial_id INTEGER REFERENCES commercial(id),
    client_id INTEGER REFERENCES client(id),
    reference VARCHAR(50) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, reference)
);

CREATE TABLE store (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, code)
);

CREATE TABLE cash_register (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    store_id INTEGER NOT NULL REFERENCES store(id),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, store_id, code)
);

CREATE TABLE product_stock (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    product_id INTEGER NOT NULL REFERENCES product(id),
    store_id INTEGER REFERENCES store(id),
    quantity INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, product_id, store_id)
);

CREATE TABLE activity_log (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    user_id INTEGER REFERENCES "user"(id),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX idx_client_org ON client(organization_id);
CREATE INDEX idx_product_org ON product(organization_id);
CREATE INDEX idx_sale_org ON sale(organization_id);
CREATE INDEX idx_store_org ON store(organization_id);
CREATE INDEX idx_activity_org ON activity_log(organization_id);
```

---

## 🔐 Sécurité Multi-Tenant

### Règle 1 : Tous les accès sont filtrés par organization_id

```python
# ✅ BON
clients = Client.query.filter(
    Client.organization_id == current_org.id
).all()

# ❌ MAUVAIS
clients = Client.query.all()
```

### Règle 2 : Les URLs ne doivent pas contenir d'IDs modifiables

```python
# ✅ BON : L'organization est déterminée du contexte
GET /api/v1/clients

# ❌ MAUVAIS : Un utilisateur pourrait modifier l'org_id
GET /api/v1/organizations/123/clients
```

### Règle 3 : Validation de permissions à chaque requête

```python
@app.before_request
def check_tenant_access():
    user = get_current_user()
    current_org = get_current_organization()
    
    # Vérifier que l'utilisateur a accès à cette organization
    if not user.has_organization(current_org.id):
        abort(403)
```

---

## 🚀 Déploiement et Scalabilité

### Phase 1 : Shared Database / Shared Schema
- Une base unique
- Performances optimales au démarrage
- Le moins complexe à mettre en place

### Phase 2 : Shared Database / Schema per Tenant
- Une base, plusieurs schémas
- Meilleure isolation
- Plus complexe à mettre en place

### Phase 3 : Database per Tenant
- Une base par tenant
- Isolation maximale
- Nécessaire pour les clients Enterprise

---

## 📊 Monitoring et Logging

### Activity Log

Toutes les actions critiques doivent être loggées :

```python
ActivityLog.create(
    organization_id=current_org.id,
    user_id=current_user.id,
    action='create_sale',
    resource_type='sale',
    resource_id=sale.id,
    ip_address=request.remote_addr,
    metadata={'amount': 25000, 'items': 3}
)
```

### Alertes de Sécurité

```
- Tentative de cross-tenant access → Alerte
- Annulation fréquente de ventes → Alerte
- Remboursement suspect → Alerte
- Écart de caisse important → Alerte
- Modification de prix non autorisée → Alerte
```

---

## 🧪 Testing par Couche

| Couche | Test | Exemple |
|--------|------|---------|
| Models | Unit | `test_client_model.py` |
| Repository | Integration | `test_client_repository.py` |
| Service | Unit | `test_client_service.py` |
| API | Integration | `test_client_api.py` |
| Multi-Tenant | Integration | `test_tenant_isolation.py` |

---

## 📚 Documentation par Module

Chaque module devra avoir :
- `/module/README.md` - Vue d'ensemble
- `/module/MODELS.md` - Modèles de données
- `/module/API.md` - Endpoints API
- `/module/WORKFLOW.md` - Workflow métier

---

**Prochaine étape :** Voir [DATABASE.md](./DATABASE.md) pour le schéma détaillé.
