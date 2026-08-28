# Structure Complète du Projet AFRIVA SaaS

Voici la structure complète du projet à mettre en place sur GitHub :

```
afriva-saas/
│
├── app/                                    # Application principale
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── base.py                        # Configuration de base
│   │   ├── development.py
│   │   ├── staging.py
│   │   └── production.py
│   │
│   ├── middleware/                        # Middlewares Flask
│   │   ├── __init__.py
│   │   ├── tenant_middleware.py           # Multi-tenant context
│   │   ├── auth_middleware.py             # Authentification
│   │   ├── permission_middleware.py       # Vérification permissions
│   │   ├── rate_limit_middleware.py       # Rate limiting
│   │   ├── security_middleware.py         # Headers sécurité
│   │   ├── error_handler.py               # Gestion erreurs
│   │   └── cors_middleware.py             # CORS
│   │
│   ├── models/                            # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py                        # Classe de base
│   │   ├── user.py                        # User, OrganizationUser
│   │   ├── organization.py                # Organization
│   │   ├── role.py                        # Role, Permission
│   │   ├── crm.py                         # Client, Prospect, Visit, etc.
│   │   ├── commercial.py                  # Commercial
│   │   ├── product.py                     # Product, ProductCategory
│   │   ├── sales.py                       # Sale, SaleItem
│   │   ├── pos.py                         # Store, CashRegister, CashSession, Receipt
│   │   ├── payment.py                     # Payment, Refund
│   │   ├── inventory.py                   # ProductStock, StockMovement, Inventory
│   │   ├── billing.py                     # Plan, Subscription, Invoice
│   │   ├── objective.py                   # Objective, Performance
│   │   └── audit.py                       # ActivityLog
│   │
│   ├── services/                          # Logique métier
│   │   ├── __init__.py
│   │   ├── base_service.py                # Service de base tenant-aware
│   │   ├── auth_service.py
│   │   ├── tenant_service.py
│   │   ├── user_service.py
│   │   ├── organization_service.py
│   │   ├── client_service.py
│   │   ├── commercial_service.py
│   │   ├── sales_service.py
│   │   ├── pos_service.py
│   │   ├── cash_service.py
│   │   ├── payment_service.py
│   │   ├── inventory_service.py
│   │   ├── stock_service.py
│   │   ├── product_service.py
│   │   ├── billing_service.py
│   │   ├── subscription_service.py
│   │   ├── report_service.py
│   │   ├── analytics_service.py
│   │   ├── notification_service.py
│   │   ├── import_service.py              # Import Excel
│   │   └── export_service.py              # Export Excel/PDF/CSV
│   │
│   ├── repositories/                      # Accès aux données
│   │   ├── __init__.py
│   │   ├── base_repository.py             # Repository de base (tenant-aware)
│   │   ├── user_repository.py
│   │   ├── organization_repository.py
│   │   ├── client_repository.py
│   │   ├── product_repository.py
│   │   ├── sales_repository.py
│   │   ├── pos_repository.py
│   │   ├── inventory_repository.py
│   │   ├── billing_repository.py
│   │   ├── activity_log_repository.py
│   │   └── report_repository.py
│   │
│   ├── permissions/                       # RBAC (Role-Based Access Control)
│   │   ├── __init__.py
│   │   ├── decorators.py                  # @require_permission
│   │   ├── default_roles.py               # Rôles par défaut
│   │   ├── default_permissions.py         # Permissions par défaut
│   │   └── utils.py                       # Vérification permissions
│   │
│   ├── utils/                             # Utilitaires
│   │   ├── __init__.py
│   │   ├── decorators.py                  # Décorateurs custom
│   │   ├── validators.py                  # Validateurs métier
│   │   ├── formatters.py                  # Formatage (devise, date)
│   │   ├── file_handlers.py               # Gestion des fichiers
│   │   ├── email_sender.py                # Envoi emails
│   │   ├── sms_sender.py                  # Envoi SMS
│   │   ├── cache.py                       # Cache tenant-aware
│   │   ├── response.py                    # Réponses JSON standard
│   │   ├── exceptions.py                  # Exceptions custom
│   │   └── constants.py                   # Constantes globales
│   │
│   ├── auth/                              # Module authentification
│   │   ├── __init__.py
│   │   ├── routes.py                      # /auth endpoints
│   │   ├── forms.py                       # Validation formulaires
│   │   └── decorators.py                  # @login_required, etc.
│   │
│   ├── tenants/                           # Module multi-tenant
│   │   ├── __init__.py
│   │   ├── routes.py                      # /organizations endpoints
│   │   ├── forms.py
│   │   └── context.py                     # TenantContext
│   │
│   ├── users/                             # Module utilisateurs
│   │   ├── __init__.py
│   │   ├── routes.py                      # /users endpoints
│   │   └── forms.py
│   │
│   ├── crm/                               # Module CRM
│   │   ├── __init__.py
│   │   ├── routes.py                      # /crm endpoints
│   │   ├── forms.py
│   │   └── utils.py
│   │
│   ├── sales/                             # Module Ventes
│   │   ├── __init__.py
│   │   ├── routes.py                      # /sales endpoints
│   │   └── forms.py
│   │
│   ├── pos/                               # Module POS
│   │   ├── __init__.py
│   │   ├── routes.py                      # /pos endpoints
│   │   ├── forms.py
│   │   ├── cash_handler.py                # Gestion caisse
│   │   ├── receipt_generator.py           # Génération tickets
│   │   └── printer.py                     # Intégration imprimante
│   │
│   ├── inventory/                         # Module Stocks
│   │   ├── __init__.py
│   │   ├── routes.py                      # /inventory endpoints
│   │   ├── forms.py
│   │   └── stock_handler.py               # Gestion stocks
│   │
│   ├── billing/                           # Module Facturation
│   │   ├── __init__.py
│   │   ├── routes.py                      # /billing endpoints
│   │   ├── forms.py
│   │   ├── providers/                     # Fournisseurs de paiement
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── stripe.py
│   │   │   ├── paypal.py
│   │   │   └── local_providers.py
│   │   └── webhooks.py                    # Webhooks paiements
│   │
│   ├── reports/                           # Module Rapports
│   │   ├── __init__.py
│   │   ├── routes.py                      # /reports endpoints
│   │   ├── generators/                    # Générateurs rapports
│   │   │   ├── sales_report.py
│   │   │   ├── pos_report.py
│   │   │   ├── stock_report.py
│   │   │   └── client_report.py
│   │   └── exporters/                     # Exporteurs
│   │       ├── excel_exporter.py
│   │       ├── pdf_exporter.py
│   │       └── csv_exporter.py
│   │
│   ├── analytics/                         # Module BI
│   │   ├── __init__.py
│   │   ├── routes.py                      # /analytics endpoints
│   │   ├── dashboards.py
│   │   └── queries.py
│   │
│   ├── admin/                             # Admin panel
│   │   ├── __init__.py
│   │   ├── routes.py                      # /admin endpoints
│   │   └── forms.py
│   │
│   ├── api/                               # API RESTful
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── organizations.py
│   │   │   ├── users.py
│   │   │   ├── clients.py
│   │   │   ├── prospects.py
│   │   │   ├── products.py
│   │   │   ├── sales.py
│   │   │   ├── pos.py
│   │   │   ├── payments.py
│   │   │   ├── inventory.py
│   │   │   ├── reports.py
│   │   │   ├── billing.py
│   │   │   ├── analytics.py
│   │   │   └── webhooks.py
│   │   └── v2/                            # Future
│   │
│   ├── jobs/                              # Jobs asynchrones (Celery)
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── email_jobs.py
│   │   ├── report_jobs.py
│   │   ├── billing_jobs.py
│   │   ├── import_jobs.py
│   │   └── notification_jobs.py
│   │
│   ├── templates/                         # Templates Jinja2
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── forgot_password.html
│   │   ├── dashboard/
│   │   │   ├── enterprise_dashboard.html
│   │   │   ├── pos_dashboard.html
│   │   │   └── commercial_dashboard.html
│   │   ├── crm/
│   │   ├── pos/
│   │   ├── inventory/
│   │   ├── reports/
│   │   └── errors/
│   │       ├── 403.html
│   │       ├── 404.html
│   │       └── 500.html
│   │
│   ├── static/                            # Fichiers statiques
│   │   ├── css/
│   │   │   ├── bootstrap.min.css
│   │   │   ├── custom.css
│   │   │   └── dashboard.css
│   │   ├── js/
│   │   │   ├── bootstrap.min.js
│   │   │   ├── chart.min.js
│   │   │   ├── app.js
│   │   │   └── api.js
│   │   ├── images/
│   │   │   └── logo.png
│   │   └── fonts/
│   │
│   └── tasks/                             # Tâches de maintenance
│       ├── __init__.py
│       ├── init_db.py
│       ├── seed.py
│       └── health_check.py
│
├── migrations/                            # Migrations Alembic
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_add_multi_tenant.py
│       └── ...
│
├── tests/                                 # Tests
│   ├── __init__.py
│   ├── conftest.py                        # Configuration pytest
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── auth_fixtures.py
│   │   ├── tenant_fixtures.py
│   │   ├── user_fixtures.py
│   │   ├── client_fixtures.py
│   │   ├── product_fixtures.py
│   │   └── pos_fixtures.py
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_client_service.py
│   │   ├── test_inventory_service.py
│   │   └── ...
│   ├── integration/
│   │   ├── test_auth_flow.py
│   │   ├── test_pos_workflow.py
│   │   ├── test_stock_management.py
│   │   └── ...
│   └── security/
│       ├── test_tenant_isolation.py
│       ├── test_permission_checks.py
│       └── test_cross_tenant_access.py
│
├── docs/                                  # Documentation
│   ├── README.md                          # Renvoie au README.md root
│   ├── ARCHITECTURE.md
│   ├── DATABASE.md
│   ├── MULTI_TENANCY.md
│   ├── API.md
│   ├── SECURITY.md
│   ├── DEPLOYMENT.md
│   ├── TESTING.md
│   ├── DEVELOPMENT_PLAN.md
│   ├── GUIDES/
│   │   ├── setup.md
│   │   ├── first_run.md
│   │   ├── multi_tenant_guide.md
│   │   └── pos_setup.md
│   ├── API_ENDPOINTS.md
│   └── TROUBLESHOOTING.md
│
├── docker/                                # Docker
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── nginx.conf
│   └── .dockerignore
│
├── scripts/                               # Scripts utiles
│   ├── init_db.sh
│   ├── seed_data.sh
│   ├── backup.sh
│   ├── restore.sh
│   ├── deploy.sh
│   └── health_check.sh
│
├── .github/                               # GitHub
│   ├── workflows/
│   │   ├── ci-cd.yml                      # CI/CD pipeline
│   │   ├── tests.yml                      # Tests
│   │   └── security-scan.yml              # Scan sécurité
│   ├── ISSUE_TEMPLATE/
│   │   └── bug_report.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── .env.example                           # Variables d'environnement
├── .gitignore                             # Git ignore
├── .flake8                                # Linting
├── pytest.ini                             # Pytest config
├── setup.py                               # Setup Python
├── wsgi.py                                # Point d'entrée WSGI
├── requirements.txt                       # Dépendances
├── requirements-dev.txt                   # Dépendances dev
├── README.md                              # Readme principal
├── CHANGELOG.md                           # Historique
├── LICENSE                                # MIT License
└── CONTRIBUTING.md                        # Guide contribution
```

---

## 📝 Créer les Fichiers Manquants

Pour démarrer rapidement, voici les commandes :

```bash
# Cloner le repo
git clone https://github.com/yourusername/afriva-saas.git
cd afriva-saas

# Créer la structure de dossiers
mkdir -p app/{config,middleware,models,services,repositories,permissions,utils}
mkdir -p app/{auth,tenants,users,crm,sales,pos,inventory,billing,reports,analytics,admin,api/v1,jobs,templates,static/{css,js,images,fonts},tasks}
mkdir -p migrations/versions
mkdir -p tests/{unit,integration,security,fixtures}
mkdir -p docs/GUIDES
mkdir -p docker
mkdir -p scripts
mkdir -p .github/{workflows,ISSUE_TEMPLATE}

# Créer les fichiers __init__.py
touch app/__init__.py
touch app/config/__init__.py
touch app/middleware/__init__.py
# ... etc pour tous les dossiers

# Créer les fichiers de configuration
cp .env.example .env
touch .flake8
touch pytest.ini
touch setup.py
touch wsgi.py
```

---

## 🔑 Fichiers Prioritaires à Créer en Premier

### Phase 1 (Semaine 1)
1. ✅ README.md
2. ✅ ARCHITECTURE.md
3. ✅ .env.example
4. ✅ requirements.txt
5. ✅ PROJECT_STRUCTURE.md (ce fichier)
6. 📄 .gitignore
7. 📄 setup.py

### Phase 2 (Semaine 2)
8. 📄 app/__init__.py (configuration Flask)
9. 📄 wsgi.py (entry point)
10. 📄 migrations (structure Alembic)
11. 📄 MULTI_TENANCY_PLAN.md

### Phase 3 (Semaines 3-4)
12. 📄 app/models/base.py
13. 📄 app/models/user.py
14. 📄 app/models/organization.py
15. 📄 app/services/base_service.py
16. 📄 app/repositories/base_repository.py
17. 📄 app/middleware/tenant_middleware.py
18. 📄 app/permissions/decorators.py
19. 📄 tests/test_tenant_isolation.py

---

## 🎯 Commandes de Démarrage

```bash
# 1. Setup environnement
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Setup base de données
flask db init
flask db migrate -m "Initial schema"
flask db upgrade

# 3. Seed data (optionnel)
flask seed

# 4. Lancer le serveur
flask run
```

---

## 📦 Fichiers de Configuration Essentiels

### setup.py
```python
from setuptools import setup, find_packages

setup(
    name='afriva-saas',
    version='0.1.0',
    description='AFRIVA SaaS Platform',
    author='Your Name',
    author_email='your@email.com',
    url='https://github.com/yourusername/afriva-saas',
    packages=find_packages(),
    install_requires=[
        'Flask==2.3.2',
        'Flask-SQLAlchemy==3.0.5',
        'Flask-Login==0.6.2',
        'Flask-JWT-Extended==4.4.4',
        'SQLAlchemy==2.0.19',
        'psycopg2-binary==2.9.6',
        'alembic==1.11.1',
        'marshmallow==3.19.0',
        'python-dotenv==1.0.0',
        'bcrypt==4.0.1',
        'redis==4.6.0',
        'celery==5.3.1',
        'stripe==5.15.0',
        'boto3==1.28.13',
        'requests==2.31.0',
    ],
    extras_require={
        'dev': [
            'pytest==7.4.0',
            'pytest-cov==4.1.0',
            'pytest-flask==1.2.0',
            'flake8==6.0.0',
            'black==23.7.0',
            'isort==5.12.0',
        ]
    },
    python_requires='>=3.9',
)
```

### wsgi.py
```python
import os
from app import create_app, db

config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
```

### .gitignore
```
# Virtual Environment
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Media
uploads/
media/

# Cache
.cache/
.pytest_cache/
.coverage

# OS
.DS_Store
Thumbs.db

# Testing
.tox/
coverage.xml
*.cover

# Production
.env.production
*.key
*.pem
```

---

## ✅ Checklist de Mise en Place

- [ ] Repository créé sur GitHub
- [ ] Structure de dossiers créée
- [ ] Fichiers principaux (README, ARCHITECTURE, etc.)
- [ ] .env.example et .gitignore
- [ ] requirements.txt
- [ ] setup.py et wsgi.py
- [ ] CI/CD workflow (GitHub Actions)
- [ ] Protection de la branche main
- [ ] Documentation basique
- [ ] Premier commit sur develop

---

## 🚀 Prochaines Étapes

1. Créer tous les fichiers de cette structure
2. Initialiser Git et pousser sur GitHub
3. Configurer les branches (main, develop)
4. Mettre en place CI/CD (GitHub Actions)
5. Commencer Phase 1 (Audit)

**Voir [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) pour le plan détaillé.**
