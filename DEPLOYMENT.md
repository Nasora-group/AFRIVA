# AFRIVA SaaS — Deployment & Release Guide

## 1. Objectif

Ce document définit la procédure de préparation, validation et déploiement d'AFRIVA SaaS. Il privilégie d'abord un environnement **staging** et interdit toute modification directe de la production pendant la validation.

## 2. Pré-requis

- Python 3.11
- PostgreSQL 16 (compatible avec la CI)
- Variables d'environnement configurées hors du dépôt
- Sauvegarde PostgreSQL disponible avant toute migration de production
- HTTPS activé en production
- Accès aux logs et au health check de l'application

## 3. Pipeline de release

1. Développer sur une branche `phase*/*`.
2. Ouvrir une Pull Request vers `main`.
3. Attendre une CI entièrement verte : tests, couverture, Flake8, Black, isort et contrôles PostgreSQL/RLS.
4. Effectuer les smoke tests en staging.
5. Vérifier les migrations sur une copie de la base.
6. Valider la release.
7. Sauvegarder la base de production.
8. Déployer le code et appliquer les migrations.
9. Vérifier le health check et les logs.
10. Surveiller la release avant de considérer le déploiement terminé.

## 4. Variables d'environnement

Les secrets ne doivent jamais être commités. Au minimum, l'environnement de déploiement doit fournir :

```text
SECRET_KEY
DATABASE_URL
TEST_DATABASE_URL (staging/CI uniquement)
SESSION_COOKIE_SECURE=true
```

Les valeurs réelles doivent être configurées dans le gestionnaire de secrets de la plateforme d'hébergement.

## 5. Base de données et migrations

Avant production :

```bash
flask db current
flask db heads
flask db upgrade
```

La migration doit d'abord être exécutée et vérifiée en staging. Une sauvegarde exploitable doit exister avant toute migration de production.

## 6. Smoke tests staging

Vérifier au minimum :

- démarrage de l'application ;
- connexion/authentification ;
- sélection et isolation du tenant ;
- accès aux fonctions CRM/POS/stock ;
- facturation et abonnement ;
- lecture/écriture PostgreSQL ;
- absence d'erreurs 5xx dans les logs ;
- health check après migration.

## 7. Sécurité de production

- `DEBUG` désactivé ;
- secrets uniquement via variables d'environnement ;
- HTTPS obligatoire ;
- cookies sécurisés ;
- CSRF actif pour les formulaires concernés ;
- protections XSS et injection SQL conservées ;
- limitation de débit sur les endpoints sensibles ;
- logs sans mots de passe, tokens ou données sensibles.

## 8. Rollback

En cas d'incident :

1. stopper la promotion de la release ;
2. conserver les logs de l'incident ;
3. revenir au dernier commit applicatif stable ;
4. restaurer la base depuis la sauvegarde si la migration ne peut pas être rétrogradée proprement ;
5. vérifier les health checks ;
6. documenter l'incident avant une nouvelle tentative.

## 9. Checklist finale

- [ ] CI entièrement verte
- [ ] PR approuvée et fusionnée
- [ ] Tests staging réussis
- [ ] Migration testée en staging
- [ ] Backup production vérifié
- [ ] Secrets configurés
- [ ] HTTPS actif
- [ ] Health check OK
- [ ] Logs surveillés
- [ ] Procédure de rollback prête

> **Règle :** aucun déploiement production ne doit être considéré comme réussi uniquement parce que la CI est verte. La validation staging et les contrôles post-déploiement sont obligatoires.
