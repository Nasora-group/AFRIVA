# Phase 13 — Déploiement et mise en production

## Objectif
Préparer un déploiement reproductible de l'application sans modifier directement l'environnement de production.

## Contrôles
- configuration exclusivement par variables d'environnement ;
- endpoint `/health` disponible pour les probes ;
- Gunicorn comme serveur WSGI en production ;
- migrations exécutées avant le démarrage applicatif ;
- aucun secret dans le dépôt ;
- sauvegarde PostgreSQL avant migration de production ;
- déploiement d'abord en staging puis promotion vers production.

## Procédure de release
1. Construire l'image ou l'environnement applicatif depuis le commit validé.
2. Déployer en staging.
3. Exécuter les smoke tests (`/`, `/health`, authentification et parcours métier critiques).
4. Vérifier les migrations et la connectivité PostgreSQL.
5. Promouvoir exactement le même artefact en production.
6. Vérifier `/health` et les journaux après déploiement.
7. Conserver le commit précédent pour rollback.

La CI reste informative selon la méthode de validation adoptée pour le projet : elle ne remplace pas les contrôles fonctionnels et de sécurité.
