# Plan de Développement - AFRIVA SaaS

## 📅 Chronologie Globale

**Durée estimée :** 24 semaines (6 mois)  
**Équipe recommandée :** 3-5 développeurs + 1 architect

---

## 🚀 Phase 1 : Audit & Planification (Semaine 1)

### Objectifs
- Analyser le code existant
- Identifier les risques
- Évaluer la migration

### Tâches

#### 1.1 Analyse du Repository
```bash
# Fichiers à analyser :
- Structure existante
- Modèles SQLAlchemy
- Routes Flask
- Migrations Alembic
- Configuration
- Dépendances (requirements.txt)
```

#### 1.2 Analyse de la Base de Données
```sql
-- Examiner les tables existantes
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Identifier les relations
-- Identifier les données existantes
-- Évaluer les migrations nécessaires
```

#### 1.3 Analyse de Sécurité
- Authentification existante
- Gestion des sessions
- Permissions actuelles
- Failles potentielles

#### 1.4 Livrables
- **AUDIT.md** - Rapport complet d'audit
- Liste des fonctionnalités existantes
- Évaluation des risques
- Recommandations

### Effort estimé
- 3-5 jours (1 architecte + 1 développeur senior)

---

## 🏗️ Phase 2 : Architecture Multi-Tenant (Semaine 2)

### Objectifs
- Concevoir le système multi-tenant
- Planifier la migration
- Valider l'architecture

### Tâches

#### 2.1 Concevoir le Système de Tenant
```
Actuellement :
- Une seule "entreprise" ou application mono-tenant

À devenir :
- Un système où plusieurs organizations partagent la plateforme
- Chaque organization a ses propres données
- Un utilisateur peut appartenir à plusieurs organizations
```

#### 2.2 Migration des Données
```python
# Avant (mono-tenant) :
User
  └── roles
  └── permissions

# Après (multi-tenant) :
User
  └── OrganizationUser
      ├── organization_id
      ├── role_id (pour cette org)
      └── permissions (pour cette org)
```

#### 2.3 Architecture du Tenant Context
```python
# Dans chaque requête, le contexte du tenant doit être disponible :
current_organization = get_current_organization()
current_user = get_current_user()
current_permissions = get_current_permissions()
```

#### 2.4 Stratégie de Base de Données
- Rester sur **Shared Database / Shared Schema** pour V1
- Ajouter `organization_id` à toutes les tables métier
- Prévoir l'évolution ultérieure

#### 2.5 Livrables
- **MULTI_TENANCY_PLAN.md** - Plan détaillé de migration
- **DATABASE_MIGRATION_STRATEGY.md** - Stratégie des migrations
- Diagramme de transition
- Checklist de validation

### Effort estimé
- 3-5 jours (1 architecte + 1 architecte DB)

---

## 🔐 Phase 3 : Socle Multi-Tenant (Semaines 3-4)

### Objectifs
- Implémenter les foundations
- Sécuriser l'isolation des données
- Préparer les phases suivantes

### Tâches

#### 3.1 Modèles Fondamentaux
```python
# À créer/modifier :
- Organization (nouvelle table)
- User (adapter)
- OrganizationUser (nouvelle table)
- Role (adapter si nécessaire)
- Permission (adapter si nécessaire)
```

#### 3.2 Middleware Tenant Context
```python
# Créer : app/middleware/tenant_middleware.py
# Responsabilités :
- Identifier le tenant courant
- Charger le contexte
- Stocker dans g (Flask globals)
- Valider l'accès
```

#### 3.3 Système de Permissions RBAC
```python
# Créer : app/permissions/
# - Rôles par défaut (Super Admin, Owner, Manager, etc.)
# - Permissions (clients.view, sales.create, etc.)
# - Décorateurs (@require_permission)
# - Vérification in-template
```

#### 3.4 Repository Tenant-Aware
```python
# Créer : app/repositories/base_repository.py
# - Tous les repositories héritent de BaseRepository
# - Filtrage automatique par organization_id
# - Requêtes sûres par défaut
```

#### 3.5 Tests Multi-Tenant
```python
# Créer : tests/test_tenant_isolation.py
# - Org A ne peut pas accéder aux données de Org B
# - Tests pour chaque entité
# - Couverture complète
```

#### 3.6 Migration de la Base
```bash
# Fichiers à créer :
- alembic/versions/001_add_organization.py
- alembic/versions/002_add_organization_id_to_users.py
- alembic/versions/003_add_organization_id_to_all_tables.py
# etc.
```

#### 3.7 Authentification Améliorée
- Session du tenant dans la session utilisateur
- Sélection de l'organization à la connexion
- Changement d'organization dynamique

#### 3.8 Livrables
- Code fonctionnel multi-tenant
- Migrations appliquées
- Tests passants (>80% couverture)
- Documentation des patterns

### Effort estimé
- 10-15 jours (2 développeurs)

### Checklist de Validation
- [ ] Tous les tests multi-tenant passent
- [ ] Une org ne peut pas voir les données d'une autre
- [ ] Les permissions sont correctement appliquées
- [ ] Les migrations s'exécutent sans erreur
- [ ] La base de données est cohérente

---

## 📞 Phase 4 : CRM (Semaines 5-7)

### Objectifs
- Implémenter le module CRM complet
- Gestion des clients, prospects, contacts
- Visites et prospections

### Modèles à Créer
```
- Commercial (vendeur)
- Client
- Prospect
- Contact
- Visit
- Prospection
- Tour (tournée)
- TourStop
- Task
- Note
```

### Fonctionnalités

#### Clients
- Fiche complète (raison sociale, type, secteur)
- Historique des visites
- Historique des ventes
- CA client
- Produits achetés
- Statut et observations
- Géolocalisation

#### Prospects
- Statuts (nouveau, contacté, en cours, intéressé, client, perdu)
- Informations de base
- Suivi de prospection
- Conversion en client

#### Visites
- Date, heure, durée
- Localisation GPS
- Objectif et résultat
- Produits présentés
- Commande
- Notes

#### Prospections
- Motif
- Interlocuteur
- Potentiel
- Prochaine action
- Relance

#### Tournées
- Sélection des clients
- Planification
- Carte interactive
- Suivi en temps réel

### API Endpoints
```
GET    /api/v1/crm/commercials
GET    /api/v1/crm/clients
POST   /api/v1/crm/clients
GET    /api/v1/crm/clients/{id}
PUT    /api/v1/crm/clients/{id}

GET    /api/v1/crm/prospects
POST   /api/v1/crm/prospects
PUT    /api/v1/crm/prospects/{id}

GET    /api/v1/crm/visits
POST   /api/v1/crm/visits
GET    /api/v1/crm/clients/{id}/visits

GET    /api/v1/crm/prospections
POST   /api/v1/crm/prospections

GET    /api/v1/crm/tours
POST   /api/v1/crm/tours/{id}/start
POST   /api/v1/crm/tours/{id}/stop/{clientId}
```

### Tests
```python
- test_client_creation.py
- test_client_geolocation.py
- test_prospect_workflow.py
- test_visit_tracking.py
- test_tour_management.py
- test_crm_multi_tenant.py
```

### Effort estimé
- 15-20 jours (2 développeurs)

---

## 💼 Phase 5 : Ventes Commerciales (Semaines 8-9)

### Objectifs
- Ventes terrain
- Objectifs commerciaux
- Performances

### Modèles
```
- Sale (vente commerciale)
- SaleItem
- Objective
- Performance
- Evaluation
- DailyReport
```

### Fonctionnalités

#### Ventes
- Vente rapide (client, produits, quantités, remise, prix)
- Statuts (brouillon, confirmée, expédiée, payée)
- Historique modifications
- Lien avec POS si applicable

#### Objectifs
- Par commercial, équipe, magasin
- Mensuel, trimestriel, annuel
- Suivi en temps réel
- Écarts visualisés

#### Performances
- CA par commercial
- Nombre de visites
- Nombre de prospects
- Taux de conversion
- Produits vendus

### API Endpoints
```
GET    /api/v1/sales
POST   /api/v1/sales
GET    /api/v1/sales/{id}
PUT    /api/v1/sales/{id}

GET    /api/v1/objectives
POST   /api/v1/objectives
PUT    /api/v1/objectives/{id}

GET    /api/v1/performance/commercial/{id}
GET    /api/v1/performance/team/{id}
```

### Effort estimé
- 10-12 jours (1-2 développeurs)

---

## 🛒 Phase 6 : POS / Caisse (Semaines 10-13)

### Objectifs
- Module POS complet
- Paiements multimodaux
- Tickets thermiques
- Clôture de caisse

### Modèles
```
- Store (magasin)
- CashRegister (caisse)
- CashSession (session de caisse)
- Sale (vente POS)
- Payment (paiement)
- Refund (remboursement)
- Receipt (ticket)
- CashIn (entrée)
- CashOut (sortie)
```

### Workflow POS

```
1. Ouverture Caisse
   - Caissier saisit le fond initial
   - Session ouverte
   - Date/heure enregistrées

2. Vente
   - Scan produit ou recherche manuelle
   - Ajout au panier
   - Modification quantité
   - Application remise (si autorisée)
   - Sélection client (optionnel)
   - Ajout notes (optionnel)

3. Paiement
   - Choix du mode (espèces, carte, mobile money, chèque, mixte)
   - Calcul automatique de la monnaie
   - Validation paiement

4. Post-Paiement
   - Génération ticket (thermique/PDF/email)
   - Mise à jour stock
   - Enregistrement en base

5. Annulation/Retour
   - Création de retour
   - Remboursement
   - Mise à jour stock

6. Clôture Caisse
   - Comptage physique
   - Comparaison solde théorique
   - Gestion des écarts
   - Rapport de clôture
   - Session fermée
```

### Fonctionnalités

#### Interface POS
- Recherche produit rapide
- Scanner code-barres (USB/Bluetooth/webcam)
- Panier éditeur en temps réel
- Remise produit/panier
- Calcul TTC automatique
- Total en gros caractères
- Confirmation requise avant paiement

#### Paiements
- Espèces (avec calcul monnaie)
- Carte bancaire
- Mobile Money (Orange Money, Wizall, etc.)
- Chèque
- Paiement mixte
- Crédit client

#### Tickets
- Format thermique (58 mm, 80 mm)
- Impression automatique
- PDF téléchargeable
- Envoi email
- Logo entreprise
- Numérotation unique
- Détails complets (produits, remise, taxes, paiement)

#### Session de Caisse
- Ouverture avec fond initial
- Suivi des ventes en temps réel
- Comptage à la clôture
- Gestion des écarts (tolérance configurable)
- Rapport détaillé

#### Sécurité POS
- Pas de suppression de vente (seulement annulation)
- Piste d'audit complète
- Alertes anomalies (annulations fréquentes, remises élevées)
- Contrôle des modifications de prix
- Validation des rôles

### API Endpoints
```
POST   /api/v1/pos/stores
GET    /api/v1/pos/stores/{storeId}/cash-registers
POST   /api/v1/pos/cash-sessions
POST   /api/v1/pos/cash-sessions/{id}/open
POST   /api/v1/pos/sales
POST   /api/v1/pos/sales/{id}/payment
POST   /api/v1/pos/sales/{id}/refund
POST   /api/v1/pos/cash-sessions/{id}/close
GET    /api/v1/pos/cash-sessions/{id}/report
```

### Tests
```python
- test_pos_workflow.py
- test_payment_modes.py
- test_cash_session_management.py
- test_cash_reconciliation.py
- test_security_pos.py
```

### Effort estimé
- 20-25 jours (2-3 développeurs)

---

## 📦 Phase 7 : Gestion des Stocks (Semaines 14-16)

### Objectifs
- Stocks multi-magasins
- Inventaires
- Transferts
- Support pharmacie

### Modèles
```
- Product (adapté)
- ProductCategory
- ProductStock
- StockMovement
- Inventory
- InventoryItem
- StockTransfer
- ProductBatch (pharmacie)
```

### Fonctionnalités

#### Produits
- SKU unique
- Code-barres
- Prix achat/vente
- Taxes
- Catégories
- Marques
- Stock alerte

#### Stocks Multi-Magasins
```
Produit X
├── Dakar : 100 unités
├── Thiès : 45 unités
└── Touba : 20 unités
```

#### Mouvements de Stock
- Vente → Stock -
- Achat → Stock +
- Retour → Stock +
- Ajustement → Stock +/-
- Transfert → Stock A -  / Stock B +

#### Inventaires
- Inventaire manuel par magasin
- Scanner intégré
- Détection écarts
- Rapport écart
- Validation
- Historique

#### Transferts
```
Workflow :
- Demande (magasin A → magasin B)
- Validation (Stock Manager)
- Expédition (magasin A)
- Réception (magasin B)
- Finalisation
```

#### Pharmacie (Mode FEFO)
- Gestion des lots
- Date d'expiration
- Alertes expiration (30j, 60j, 90j)
- Priorité FEFO (First Expired First Out)
- Traçabilité complète

### API Endpoints
```
GET    /api/v1/inventory/products
POST   /api/v1/inventory/products
GET    /api/v1/inventory/stocks?storeId=X
PUT    /api/v1/inventory/stocks/{id}
POST   /api/v1/inventory/movements
GET    /api/v1/inventory/movements?storeId=X
POST   /api/v1/inventory/inventories
GET    /api/v1/inventory/inventories/{id}
POST   /api/v1/inventory/transfers
```

### Tests
```python
- test_stock_management.py
- test_multi_store_stock.py
- test_inventory_workflow.py
- test_stock_transfers.py
- test_pharmacy_batch_management.py
```

### Effort estimé
- 15-20 jours (2 développeurs)

---

## 💳 Phase 8 : Facturation SaaS (Semaines 17-18)

### Objectifs
- Plans d'abonnement
- Essai gratuit
- Facturation récurrente
- Quotas

### Modèles
```
- Plan
- Subscription
- Invoice
- Payment
- UsageLog
```

### Plans Proposés

| Plan | Utilisateurs | Ventes/mois | CA | Prix/mois |
|------|--------------|-------------|----|----|
| FREE | 1 | 100 | Limité | Gratuit |
| STARTER | 5 | 1000 | €29 | |
| BUSINESS | 10 | 10000 | €99 | |
| PROFESSIONAL | 25 | ∞ | €299 | |
| ENTERPRISE | ∞ | ∞ | Devis | |

### Fonctionnalités

#### Essai Gratuit
- 14 jours configurable
- Données préservées après expiration
- Upgrade simple

#### Abonnements
- Cycle mensuel/annuel
- Renouvellement automatique
- Pausing/reprendre
- Upgrade/Downgrade
- Annulation

#### Facturation
- Factures générées automatiquement
- Email de facture
- PDF téléchargeable
- Historique complet

#### Paiements
```
- Stripe (cartes de crédit)
- PayPal
- Solutions locales (Orange Money, Wave, etc.)
- Paiement manuel (Enterprise)
```

#### Quotas & Limite
- Nombre d'utilisateurs
- Nombre de ventes/mois
- Espace stockage
- API calls/jour
- Fonctionnalités selon le plan

### API Endpoints
```
GET    /api/v1/billing/plans
GET    /api/v1/billing/subscription
POST   /api/v1/billing/subscription
PUT    /api/v1/billing/subscription
POST   /api/v1/billing/subscription/upgrade
POST   /api/v1/billing/subscription/cancel

GET    /api/v1/billing/invoices
GET    /api/v1/billing/invoices/{id}/pdf

POST   /api/v1/billing/payment-methods
GET    /api/v1/billing/payment-methods

POST   /stripe/webhook
POST   /paypal/webhook
```

### Jobs Asynchrones
```python
# Nécessaire :
- Génération factures
- Envoi factures (email)
- Renouvellement abonnements
- Vérification quotas
- Alertes expiration trial
```

### Tests
```python
- test_subscription_lifecycle.py
- test_billing_calculation.py
- test_payment_processing.py
- test_quota_enforcement.py
- test_trial_management.py
```

### Effort estimé
- 12-15 jours (1-2 développeurs)

---

## 📊 Phase 9 : Business Intelligence (Semaines 19-21)

### Objectifs
- Dashboards
- KPI
- Rapports
- Exports

### Dashboards

#### Dashboard Enterprise (Direction)
```
┌──────────────────────────────────────┐
│ CA Global                            │
│ €125,000  |  Objectif : €150,000     │
│ Taux : 83%                           │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ CA par Source                        │
│ - Ventes Commerciales : €80,000      │
│ - POS : €45,000                      │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Clients | Prospects | Visites        │
│ 150     | 45        | 320            │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Stock Critique                       │
│ - Produit A : 5 unités               │
│ - Produit B : RUPTURE                │
└──────────────────────────────────────┘
```

#### Dashboard POS (Magasins)
```
┌──────────────────────────────────────┐
│ CA Aujourd'hui                       │
│ €8,500                               │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ CA par Caisse                        │
│ Caisse 1 : €4,200  | Caisse 2 : €4,300
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Tickets | Panier moyen               │
│ 125     | €68                        │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ Annulations | Remboursements         │
│ 3           | €500                   │
└──────────────────────────────────────┘
```

#### Dashboard Commercial
```
- CA personnel
- Objectif personnel
- Visites réalisées
- Prospects convertis
- Performance vs équipe
```

### Rapports

```
- Rapport Ventes
- Rapport POS
- Rapport Caisse (clôture)
- Rapport Stocks
- Rapport Clients
- Rapport Commerciaux
- Rapport Produits
- Rapport Magasins
```

### Exports

```
- Excel (.xlsx)
- CSV
- PDF
- JSON (API)
```

### Visualisations

```
- Courbes de CA
- Histogrammes comparaisons
- Camemberts répartitions
- Tableaux croisés
- Cartes (si géolocalisation)
- Jauge (pour objectifs)
```

### Filtrage

```
- Par période (jour, semaine, mois, année)
- Par magasin
- Par commercial
- Par catégorie produit
- Par client
- Par statut
```

### Tests
```python
- test_dashboard_data.py
- test_report_generation.py
- test_export_formats.py
- test_chart_data.py
```

### Effort estimé
- 15-20 jours (2 développeurs)

---

## ✅ Phase 10 : Qualité (Semaines 22-23)

### Objectives
- Tests complets
- Performance
- Sécurité
- Monitoring

### 10.1 Tests

```bash
# Couverture cible : >85%
# Tests unitaires : services, repositories, utils
# Tests intégration : API, workflows
# Tests multi-tenant : isolation des données
# Tests performance : charge, mémoire
# Tests sécurité : injection, XSS, CSRF
```

### 10.2 Performance

```
- Temps de réponse API < 500ms
- Temps chargement page < 2s
- Gestion cache tenant-aware
- Requêtes optimisées (N+1)
- Pagination pour les listes
- Index sur organization_id
```

### 10.3 Sécurité

```
Checklist :
- [ ] Pas de données en dur (secrets en env)
- [ ] Hachage des mots de passe
- [ ] CSRF tokens
- [ ] XSS escaping
- [ ] SQL injection prevention
- [ ] Rate limiting
- [ ] CORS configuré
- [ ] HTTPS en prod
- [ ] Logs de sécurité
- [ ] Gestion des erreurs (pas d'infos sensibles)
```

### 10.4 Monitoring

```
À mettre en place :
- Logs centralisés
- Alertes erreurs
- Monitoring CPU/RAM/Disk
- Monitoring base de données
- Monitoring API
- Alertes multi-tenant isolation
- Dashboard monitoring
```

### 10.5 Documentation

```
À compléter :
- README.md ✓
- ARCHITECTURE.md ✓
- DATABASE.md
- API.md
- SECURITY.md
- TESTING.md
- DEPLOYMENT.md
- CHANGELOG.md
- Inline code comments
- Postman/Swagger API docs
```

### Effort estimé
- 10-15 jours (2 développeurs + QA)

---

## 🚀 Phase 11 : Déploiement (Semaine 24)

### Objectifs
- Environnement staging
- Tests en staging
- Déploiement production
- Monitoring en prod

### Étapes

#### 11.1 Environnement Staging
```bash
# Cloner production
# Appliquer migrations
# Vérifier tous les tests
# Smoke tests
```

#### 11.2 Déploiement Production
```bash
# 1. Backup production
# 2. Appliquer migrations
# 3. Déployer code
# 4. Vérifier health checks
# 5. Monitoring
```

#### 11.3 Plan de Rollback
```bash
# Si problème :
# 1. Revert code
# 2. Revert migrations
# 3. Restaurer backup
# 4. Alerter équipe
```

### Checklist Déploiement
- [ ] Tous les tests passent
- [ ] Migrations testé en staging
- [ ] Secrets en place
- [ ] Variables d'environnement configurées
- [ ] SSL/HTTPS activé
- [ ] Backups en place
- [ ] Monitoring configuré
- [ ] Documentation à jour
- [ ] Équipe formée
- [ ] Plan d'urgence prêt

### Effort estimé
- 3-5 jours (1-2 DevOps + 2 développeurs)

---

## 📊 Résumé des Efforts

| Phase | Semaines | Effort | Équipe |
|-------|----------|--------|--------|
| 1 - Audit | 1 | 5 jours | 2 dev |
| 2 - Architecture | 1 | 5 jours | 2 dev |
| 3 - Socle | 2 | 15 jours | 2 dev |
| 4 - CRM | 3 | 18 jours | 2 dev |
| 5 - Ventes | 2 | 10 jours | 1-2 dev |
| 6 - POS | 4 | 25 jours | 2-3 dev |
| 7 - Stock | 3 | 18 jours | 2 dev |
| 8 - Facturation | 2 | 15 jours | 1-2 dev |
| 9 - BI | 3 | 18 jours | 2 dev |
| 10 - Qualité | 2 | 12 jours | 2 dev + QA |
| 11 - Déploiement | 1 | 5 jours | 1-2 DevOps |
| **TOTAL** | **24** | **146 jours** | **2-3 dev** |

---

## 🎯 Milestones Critiques

```
Week 2:  AUDIT.md + MULTI_TENANCY_PLAN.md ✓
Week 4:  Socle multi-tenant complet ✓
Week 7:  Module CRM opérationnel ✓
Week 13: Module POS opérationnel ✓
Week 16: Gestion stock opérationnelle ✓
Week 18: Facturation SaaS opérationnelle ✓
Week 21: BI dashboards opérationnels ✓
Week 23: Tous les tests passent ✓
Week 24: Déploiement production ✓
```

---

## 🔄 Processus de Développement

### Pour chaque feature :
```
1. Créer issue GitHub
2. Créer branche feature/*
3. Implémenter avec tests
4. Push et PR
5. Code review
6. Merge en develop
7. Déploiement en staging
8. Tests en staging
9. Merge en main
10. Déploiement en production
```

### Commits GitHub :
```
feat: ajouter gestion multi-tenant
fix: corriger l'isolation des données
test: ajouter tests multi-tenant
docs: documenter l'architecture
chore: mettre à jour les dépendances
perf: optimiser requêtes clients
refactor: refactoriser repository base
```

---

## ✅ Critères de Réussite

**Phase 3 (Socle)**
- [ ] Isolation multi-tenant complète
- [ ] Tous les tests passent
- [ ] Migrations appliquées sans erreur

**Phase 6 (POS)**
- [ ] Un caissier peut ouvrir, vendre et clôturer en <5 minutes
- [ ] Stock mis à jour en temps réel
- [ ] Ticket imprimable et emailable

**Phase 9 (BI)**
- [ ] Direction peut voir le CA global en temps réel
- [ ] Rapports générables en <5 secondes

**Globalement**
- [ ] Plusieurs organizations peuvent coexister
- [ ] Données complètement isolées
- [ ] >85% couverture tests
- [ ] <500ms réponse API
- [ ] Documentation complète

---

**Prochaine étape :** Voir [MULTI_TENANCY_PLAN.md](./MULTI_TENANCY_PLAN.md) pour le plan détaillé de migration.
