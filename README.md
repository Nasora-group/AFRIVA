# AFRIVA SaaS
## Plateforme Multi-Entreprises de Gestion Commerciale, CRM, POS, Caisse, Stock et Business Intelligence

**Version:** 3.0  
**Date de création:** 28 août 2026  
**Statut:** En développement  
**Type:** SaaS B2B Multi-Tenant

---

## 📋 Vue d'ensemble

AFRIVA est une plateforme SaaS complète permettant aux entreprises (pharmacies, supermarchés, distributeurs, etc.) de gérer :

- **CRM** : Clients, prospects, contacts, visites, prospections
- **Force de vente** : Commerciaux, tournées, ventes terrain
- **POS (Caisse)** : Points de vente, caisses enregistreuses, paiements, tickets
- **Stock & Inventaire** : Gestion multi-magasins, transferts, lots, expiration
- **Business Intelligence** : Dashboards, KPI, rapports, exports
- **Facturation SaaS** : Abonnements, plans, essai gratuit

---

## 🏗️ Architecture

### Stack Technique
- **Backend** : Python / Flask / SQLAlchemy
- **Base de données** : PostgreSQL
- **Frontend** : HTML5 / CSS3 / JavaScript / Bootstrap
- **Visualisation** : Chart.js
- **API** : RESTful JSON
- **Serveur** : Gunicorn / Nginx
- **Déploiement** : Docker / CI-CD

### Architecture Multi-Tenant
```
AFRIVA SaaS (1 plateforme)
  ├── Tenant A (Entreprise A)
  │   ├── CRM
  │   ├── POS
  │   ├── Stock
  │   └── Utilisateurs
  ├── Tenant B (Entreprise B)
  │   ├── CRM
  │   ├── POS
  │   ├── Stock
  │   └── Utilisateurs
  └── Tenant C (Entreprise C)
      ├── CRM
      ├── POS
      ├── Stock
      └── Utilisateurs
```

**Règle de sécurité #1 :** Isolation absolue des données entre tenants.

---

## 📁 Structure du Projet

```
afriva-saas/
├── app/                          # Application principale
│   ├── auth/                     # Authentification & autorisation
│   ├── tenants/                  # Gestion multi-tenant
│   ├── users/                    # Gestion des utilisateurs
│   ├── organizations/            # Gestion des organisations
│   ├── billing/                  # Facturation & abonnements
│   ├── crm/                      # Module CRM
│   ├── sales/                    # Ventes commerciales
│   ├── pos/                      # Module POS / Caisse
│   ├── inventory/                # Gestion des stocks
│   ├── reports/                  # Rapports & exports
│   ├── analytics/                # Business Intelligence
│   ├── admin/                    # Admin panel
│   ├── api/                      # Routes API
│   ├── models/                   # Modèles SQLAlchemy
│   ├── services/                 # Services métier
│   ├── repositories/             # Repositories (Data Access)
│   ├── permissions/              # Gestion des permissions RBAC
│   ├── middleware/               # Middlewares
│   ├── utils/                    # Utilitaires
│   ├── templates/                # Templates Jinja2
│   ├── static/                   # Fichiers statiques (CSS, JS, images)
│   └── __init__.py
├── migrations/                   # Alembic migrations
├── tests/                        # Tests unitaires & intégration
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/                         # Documentation
├── config/                       # Configuration
│   ├── development.py
│   ├── staging.py
│   ├── production.py
│   └── __init__.py
├── scripts/                      # Scripts d'initialisation
├── docker/                       # Fichiers Docker
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/                      # GitHub workflows (CI/CD)
│   └── workflows/
│       └── ci-cd.yml
├── .env.example                  # Variables d'environnement (exemple)
├── requirements.txt              # Dépendances Python
├── setup.py                      # Configuration du projet
├── wsgi.py                       # Point d'entrée WSGI
├── pytest.ini                    # Configuration pytest
├── .gitignore
├── .flake8                       # Linting Python
├── README.md                     # Ce fichier
├── ARCHITECTURE.md               # Documentation architecture
├── DATABASE.md                   # Documentation base de données
├── MULTI_TENANCY.md              # Documentation multi-tenant
├── API.md                        # Documentation API
├── SECURITY.md                   # Guide de sécurité
├── DEPLOYMENT.md                 # Guide de déploiement
├── TESTING.md                    # Guide des tests
└── CHANGELOG.md                  # Historique des versions
```

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.9+
- PostgreSQL 12+
- Git
- Docker (optionnel)

### Installation locale

```bash
# 1. Cloner le repository
git clone https://github.com/yourusername/afriva-saas.git
cd afriva-saas

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# 5. Initialiser la base de données
flask db upgrade
flask seed

# 6. Lancer l'application
flask run
```

Application accessible sur `http://localhost:5000`

### Avec Docker

```bash
docker-compose up -d
```

---

## 📚 Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Architecture technique détaillée
- **[DATABASE.md](./DATABASE.md)** - Schéma et modèles de données
- **[MULTI_TENANCY.md](./MULTI_TENANCY.md)** - Implémentation du multi-tenant
- **[API.md](./API.md)** - Documentation des endpoints API
- **[SECURITY.md](./SECURITY.md)** - Guide de sécurité et bonnes pratiques
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Guide de déploiement
- **[TESTING.md](./TESTING.md)** - Stratégie de tests

---

## 📊 Phases de Développement

### Phase 1 : Audit (Semaine 1)
- Analyse du repo existant
- Identification des risques
- Document AUDIT.md

### Phase 2 : Architecture Multi-Tenant (Semaine 2)
- Conception du système de tenant
- Plan de migration
- Document MULTI_TENANCY_PLAN.md

### Phase 3 : Socle (Semaines 3-4)
- Organisations, utilisateurs, rôles, permissions
- Tenant context middleware
- Isolation des données

### Phase 4 : CRM (Semaines 5-7)
- Clients, prospects, contacts
- Visites, prospections, tournées

### Phase 5 : Ventes (Semaines 8-9)
- Produits, ventes terrain
- Objectifs, performances

### Phase 6 : POS (Semaines 10-13)
- Magasins, caisses, sessions
- Ventes POS, paiements, tickets
- Clôture de caisse

### Phase 7 : Stock (Semaines 14-16)
- Stocks, mouvements
- Inventaires, transferts
- Lots & expiration (pharmacie)

### Phase 8 : Facturation SaaS (Semaines 17-18)
- Plans, abonnements
- Trial, quotas
- Facturation, paiements

### Phase 9 : Business Intelligence (Semaines 19-21)
- Dashboards, KPI
- Rapports, exports
- Analytics

### Phase 10 : Qualité (Semaines 22-23)
- Tests, sécurité
- Performance, monitoring

### Phase 11 : Déploiement (Semaine 24)
- Staging, production

---

## 🔐 Sécurité

### Éléments Critiques
1. **Isolation multi-tenant** - Aucune données d'un tenant ne doit être accessible par un autre
2. **RBAC (Role-Based Access Control)** - Permissions granulaires par rôle
3. **Hachage des mots de passe** - bcrypt avec salt
4. **CSRF Protection** - Tokens sur tous les formulaires
5. **SQL Injection** - Utiliser uniquement les ORM et requêtes paramétrées
6. **XSS Protection** - Escaping en templates Jinja2
7. **Sessions sécurisées** - HttpOnly, Secure, SameSite cookies
8. **MFA** - Pour Super Admin obligatoire
9. **Secrets en variables d'environnement** - Jamais en hard-code
10. **Activity Logging** - Audit trail de toutes les actions critiques

Voir [SECURITY.md](./SECURITY.md) pour plus de détails.

---

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/unit/

# Tests intégration
pytest tests/integration/

# Tous les tests
pytest

# Avec couverture
pytest --cov=app tests/
```

Voir [TESTING.md](./TESTING.md) pour la stratégie complète.

---

## 🔄 Git Workflow

### Branches
- `main` - Production (releases)
- `develop` - Développement (prochaine release)
- `feature/*` - Nouvelles fonctionnalités
- `fix/*` - Corrections de bugs

### Commits
```
feat: ajouter gestion multi-tenant
fix: corriger l'isolation des données
test: ajouter tests multi-tenant
docs: documenter l'architecture
chore: mettre à jour les dépendances
```

### Pull Requests
- Une PR par feature
- Tests obligatoires
- Review obligatoire avant merge
- Pas de merge sur main sans staging

---

## 📦 Déploiement

- **Development** : Machine locale
- **Staging** : Environnement de test
- **Production** : Serveur de production

Voir [DEPLOYMENT.md](./DEPLOYMENT.md) pour les détails.

---

## 🤝 Contribution

1. Fork le repo
2. Créer une branche `feature/your-feature`
3. Commit avec messages clairs
4. Push et créer une PR
5. Attendre la validation

---

## 📝 Licence

MIT License - Voir LICENSE pour les détails

---

## 👥 Équipe

- **Architecture** : ChatGPT / Claude Sonnet
- **Développement** : Votre équipe
- **Support** : À définir

---

## 📞 Support

Pour les questions ou problèmes :
1. Consulter la documentation
2. Ouvrir une issue GitHub
3. Contacter l'équipe support

---

**Dernière mise à jour** : 28 août 2026  
**Prochaine révision** : À définir après Phase 1
