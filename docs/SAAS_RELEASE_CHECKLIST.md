# AFRIVA SaaS Release Checklist

## Multi-entreprise
- [ ] Organisation obligatoire sur les données métier tenant-aware.
- [ ] Un utilisateur peut appartenir à plusieurs organisations avec un rôle distinct par organisation.
- [ ] Toutes les requêtes métier appliquent le contexte d'organisation.
- [ ] Les contrôles RLS empêchent l'accès croisé entre organisations.

## Abonnements
- [ ] Essai, activation, renouvellement, expiration et annulation.
- [ ] Changement de plan sans perte du rattachement à l'organisation.
- [ ] Statut d'abonnement contrôlé côté serveur.
- [ ] Accès aux fonctionnalités refusé lorsque l'abonnement n'est plus actif.

## Quotas
- [ ] Limites utilisateurs appliquées avant création.
- [ ] Limites magasins appliquées avant création.
- [ ] Limites produits appliquées avant création.
- [ ] Les compteurs sont calculés uniquement pour l'organisation courante.
- [ ] Les dépassements sont refusés côté serveur et signalés clairement à l'interface.

## Sécurité
- [ ] Authentification obligatoire pour les espaces privés.
- [ ] Permissions vérifiées côté serveur.
- [ ] Aucun identifiant d'organisation fourni par le client ne peut contourner le contexte tenant.
- [ ] Les opérations sensibles utilisent des transactions atomiques.

## Interface
- [ ] `/` ouvre l'interface AFRIVA.
- [ ] `/health` reste disponible pour le monitoring.
- [ ] Connexion et déconnexion fonctionnent.
- [ ] Dashboard, CRM, ventes, POS, stock, transferts, analytics et billing sont accessibles selon les permissions.
- [ ] Les templates partagés ne génèrent aucune erreur Jinja.

## Livraison
- [ ] Migrations SQL exécutables sur une base PostgreSQL neuve.
- [ ] Tests automatisés verts.
- [ ] Couverture minimale respectée.
- [ ] Black, isort et Flake8 verts.
- [ ] Staging vérifié avant toute mise en production.
