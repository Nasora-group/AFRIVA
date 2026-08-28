# AFRIVA SaaS — Staging Validation Checklist

Cette checklist formalise la validation avant toute promotion en production.

## CI et code
- [ ] CI entièrement verte sur le commit validé
- [ ] Tests unitaires et intégration passants
- [ ] Flake8, Black et isort passants
- [ ] Contrôles PostgreSQL/RLS passants

## Base de données
- [ ] `flask db current` vérifié
- [ ] `flask db heads` vérifié
- [ ] `flask db upgrade` testé sur staging
- [ ] Aucun conflit de migration
- [ ] Backup/restauration testés

## Smoke tests
- [ ] Application démarre correctement
- [ ] Health check OK
- [ ] Authentification OK
- [ ] Sélection du tenant OK
- [ ] Isolation entre tenants OK
- [ ] CRM OK
- [ ] POS/caisse OK
- [ ] Stocks OK
- [ ] Facturation/abonnement OK
- [ ] PostgreSQL lecture/écriture OK
- [ ] Aucun 5xx critique dans les logs

## Sécurité
- [ ] DEBUG désactivé
- [ ] Secrets hors dépôt
- [ ] HTTPS actif
- [ ] Cookies sécurisés
- [ ] CSRF/XSS/SQLi vérifiés
- [ ] Rate limiting vérifié
- [ ] Logs sans secrets ni données sensibles

## Release
- [ ] Validation staging approuvée
- [ ] Procédure de rollback prête
- [ ] Backup production vérifié
- [ ] Feu vert explicite avant production

> Cette checklist ne déclenche aucun déploiement. Elle sert uniquement à documenter la validation staging.
