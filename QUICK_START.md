# 🚀 Guide de Démarrage Rapide - AFRIVA SaaS

Vous avez reçu l'ossature complète du projet AFRIVA SaaS. Voici comment démarrer.

---

## 📋 Ce que vous avez reçu

1. **README.md** - Vue d'ensemble du projet
2. **ARCHITECTURE.md** - Architecture technique détaillée
3. **DEVELOPMENT_PLAN.md** - Plan de développement par phases (24 semaines)
4. **PROJECT_STRUCTURE.md** - Structure complète des dossiers
5. **.env.example** - Variables d'environnement
6. **requirements.txt** - Dépendances Python
7. **Ce fichier** - Guide de démarrage

---

## ⚡ Démarrage en 5 Étapes

### Étape 1 : Créer le Repository GitHub (5 min)

```bash
# 1.1 Créer un nouveau repo sur GitHub (vide, sans README)
# https://github.com/new

# 1.2 Cloner le repo
git clone https://github.com/yourusername/afriva-saas.git
cd afriva-saas

# 1.3 Initialiser Git et faire le premier commit
git config user.email "your@email.com"
git config user.name "Your Name"

# 1.4 Ajouter les fichiers reçus
# Copier les fichiers README.md, ARCHITECTURE.md, etc.

# 1.5 Commit initial
git add .
git commit -m "chore: initial project structure and documentation"
git push -u origin main
```

### Étape 2 : Créer la Structure de Dossiers (10 min)

```bash
# 2.1 Créer les dossiers principaux
mkdir -p app/{config,middleware,models,services,repositories,permissions,utils}
mkdir -p app/{auth,tenants,users,crm,sales,pos,inventory,billing,reports,analytics,admin,api/v1,jobs,templates,static/{css,js,images,fonts},tasks}

# 2.2 Créer autres dossiers
mkdir -p migrations/versions
mkdir -p tests/{unit,integration,security,fixtures}
mkdir -p docs/GUIDES
mkdir -p docker
mkdir -p scripts
mkdir -p .github/workflows

# 2.3 Créer les fichiers __init__.py
touch app/__init__.py
touch app/config/__init__.py
touch app/middleware/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch app/repositories/__init__.py
touch app/permissions/__init__.py
touch app/utils/__init__.py
touch app/auth/__init__.py
touch app/tenants/__init__.py
touch app/users/__init__.py
touch app/crm/__init__.py
touch app/sales/__init__.py
touch app/pos/__init__.py
touch app/inventory/__init__.py
touch app/billing/__init__.py
touch app/reports/__init__.py
touch app/analytics/__init__.py
touch app/admin/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/jobs/__init__.py
touch app/tasks/__init__.py
touch tests/__init__.py
touch tests/fixtures/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/security/__init__.py
```

### Étape 3 : Configurer l'Environnement (10 min)

```bash
# 3.1 Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# 3.2 Installer les dépendances
pip install -r requirements.txt

# 3.3 Copier et configurer .env
cp .env.example .env
# Éditer .env et adapter les variables

# 3.4 Vérifier l'installation
python -c "import flask; print(f'Flask {flask.__version__}')"
```

### Étape 4 : Configurer la Base de Données (15 min)

```bash
# 4.1 Créer la BD PostgreSQL (ou utiliser SQLite pour dev local)
# PostgreSQL
createdb afriva_saas
createuser afriva -P

# 4.2 Initialiser les migrations Alembic
flask db init migrations

# 4.3 Committer les fichiers
git add .
git commit -m "chore: project structure and configuration"
git push
```

### Étape 5 : Premier Test (5 min)

```bash
# 5.1 Créer un fichier app/__init__.py minimal
cat > app/__init__.py << 'EOF'
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Charger la configuration
    if config_name == 'development':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///afriva.db'
        app.config['DEBUG'] = True
    
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-prod'
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    return app
EOF

# 5.2 Créer wsgi.py minimal
cat > wsgi.py << 'EOF'
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
EOF

# 5.3 Tester
python wsgi.py
# Accéder à http://localhost:5000
```

---

## 🎯 Prochaines Actions (Ordre d'Importance)

### 🔴 CRITIQUE (Semaine 1)

#### 1. Audit du Code Existant
**Durée:** 3-5 jours  
**Responsabilité:** Architecte Senior  

```bash
# Créer AUDIT.md et documenter:
- Structure existante
- Modèles actuels
- Routes existantes
- Problèmes de sécurité
- Points de migration
```

**Fichier à créer:** `docs/AUDIT.md`

#### 2. Plan Multi-Tenant
**Durée:** 3-5 jours  
**Responsabilité:** Architecte Senior  

```bash
# Créer MULTI_TENANCY_PLAN.md et documenter:
- Stratégie migration
- Gestion du contexte tenant
- Filtrage des données
- Validation de l'isolation
```

**Fichier à créer:** `docs/MULTI_TENANCY_PLAN.md`

### 🟠 IMPORTANT (Semaines 2-4)

#### 3. Mise en Place CI/CD
**Durée:** 2-3 jours  

```bash
# Créer .github/workflows/ci-cd.yml
# - Linter (flake8)
# - Tests (pytest)
# - Couverture (>80%)
# - Scan sécurité (bandit)
```

#### 4. Bases de Données Tenant-Aware
**Durée:** 3-5 jours  

```python
# Créer app/models/base.py
class TenantAwareMixin:
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    
# Utiliser pour tous les modèles métier
class Client(db.Model, TenantAwareMixin):
    ...
```

#### 5. Middleware Tenant Context
**Durée:** 2-3 jours  

```python
# Créer app/middleware/tenant_middleware.py
# - Identifier tenant courant
# - Valider accès utilisateur
# - Stocker dans g (Flask globals)
```

### 🟡 NORMAL (Semaines 5+)

#### 6. Modules Métier
Suivre le DEVELOPMENT_PLAN.md par phase

---

## 📊 Checklist de Mise en Place

```
INFRASTRUCTURE
☐ Repository GitHub créé
☐ Structure de dossiers créée
☐ Environnement virtuel Python
☐ Dépendances installées
☐ Base de données configurée
☐ .env configuré

DOCUMENTATION
☐ README.md
☐ ARCHITECTURE.md
☐ DEVELOPMENT_PLAN.md
☐ PROJECT_STRUCTURE.md

CONFIGURATION
☐ Git branches (main, develop)
☐ GitHub Actions / CI-CD
☐ Linting (.flake8)
☐ Testing (pytest.ini)
☐ Pre-commit hooks

DÉVELOPPEMENT - PHASE 1
☐ AUDIT.md complété
☐ MULTI_TENANCY_PLAN.md complété
☐ Risques identifiés
☐ Stratégie de migration validée

DÉVELOPPEMENT - PHASE 3
☐ Modèles tenant-aware
☐ Middleware tenant context
☐ Système RBAC
☐ Tests isolation multi-tenant
☐ Repositories tenant-aware
```

---

## 💻 Commandes Utiles

```bash
# Démarrer l'application
python wsgi.py
flask run

# Lancer les tests
pytest
pytest --cov=app tests/
pytest -v tests/

# Linter le code
flake8 app/
black app/
isort app/

# Migrations
flask db init
flask db migrate -m "Description"
flask db upgrade
flask db downgrade

# Créer utilisateur admin
flask shell
>>> from app.models import User
>>> user = User(email='admin@afriva.com', ...)
>>> db.session.add(user)
>>> db.session.commit()

# Seed data
flask seed

# Vérifier la santé
flask health-check
```

---

## 🔑 Points Clés à Retenir

### 1. **Isolation Multi-Tenant = Priorité #1**
```python
# ✅ Toujours filtrer par organization_id
clients = Client.query.filter_by(organization_id=current_org.id).all()

# ❌ JAMAIS faire ceci
clients = Client.query.all()
```

### 2. **Pas de Suppression Physique**
```python
# ✅ Utiliser soft delete ou status
sale.status = 'cancelled'

# ❌ Ne jamais faire
db.session.delete(sale)
```

### 3. **Permissions Granulaires**
```python
# ✅ Vérifier les permissions
@require_permission('clients.create')
def create_client():
    ...

# ❌ Pas juste vérifier l'utilisateur
if user:  # NON !
    ...
```

### 4. **Tests Multi-Tenant Obligatoires**
```python
# Tester que Org A ne voit pas les données de Org B
def test_org_isolation():
    org_a_client = create_client(org=org_a)
    
    # Org B ne doit pas voir
    set_current_org(org_b)
    assert not can_access(org_a_client)
```

### 5. **Logging Audit**
```python
# ✅ Logger les actions critiques
ActivityLog.create(
    organization_id=current_org.id,
    user_id=user.id,
    action='create_sale',
    resource_type='sale',
    resource_id=sale.id
)
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
# Vérifier que l'env virtuel est activé
source venv/bin/activate
# Réinstaller les dépendances
pip install -r requirements.txt
```

### "sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)"
```bash
# Vérifier que PostgreSQL est lancé
sudo service postgresql start

# Vérifier DATABASE_URL dans .env
# Vérifier que la BD existe
createdb afriva_saas
```

### Tests échouent
```bash
# Vérifier que la BD de test est créée
createdb afriva_test

# Vérifier TEST_DATABASE_URL dans .env
# Lancer les tests en verbose
pytest -v tests/
```

---

## 📞 Support & Questions

1. **Lire d'abord** les fichiers de documentation (README, ARCHITECTURE)
2. **Vérifier** le DEVELOPMENT_PLAN.md pour la phase
3. **Ouvrir une issue** sur GitHub avec détails
4. **Contacter** l'équipe si bloqué

---

## 🎓 Apprentissage et Onboarding

Nouvelle personne dans l'équipe?

1. Lire **README.md** (10 min)
2. Lire **ARCHITECTURE.md** (30 min)
3. Voir la **PROJECT_STRUCTURE** (15 min)
4. Suivre ce **QUICK_START.md** (30 min)
5. Lire **DEVELOPMENT_PLAN.md** (30 min)
6. Cloner et lancer localement (30 min)

**Total:** ~2-3 heures pour onboard complètement

---

## 🚀 Commencer Maintenant

```bash
# 1. Cloner et setup
git clone https://github.com/yourusername/afriva-saas.git
cd afriva-saas
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configurer
cp .env.example .env
# Éditer .env

# 3. Lancer
python wsgi.py

# 4. Créer premier commit
git add .
git commit -m "setup: initial environment configuration"
git push
```

---

## 📅 Prochaines Étapes Cette Semaine

- [ ] Jour 1-2: Repository GitHub + Structure + Setup local
- [ ] Jour 3-4: Audit du code existant → AUDIT.md
- [ ] Jour 5: Plan multi-tenant → MULTI_TENANCY_PLAN.md
- [ ] Jour 5: Commit et push sur main

**Semaine prochaine:** Commencer Phase 3 (Socle multi-tenant)

---

## 💡 Conseils Pratiques

1. **Commit régulièrement** - Pas de commits énormes
2. **Tests d'abord** - TDD pour les critiques
3. **Documentation vivante** - Mettre à jour docs avec le code
4. **Revues de code** - Obligatoires avant merge
5. **Pas de production d'abord** - Dev → Staging → Prod
6. **Secrets sûrs** - Jamais en git, toujours en .env
7. **Performance en tête** - Indexes, caching, optimisation queries

---

**Bienvenue dans le projet AFRIVA SaaS! 🎉**

Pour toute question, consultez la documentation ou ouvrez une issue GitHub.

**Bonne chance!** 🚀
