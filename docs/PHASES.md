# AFRIVA — état des phases

| Phase | Domaine | État |
|---|---|---|
| 6 | POS | Intégrée à `main` |
| 7 | Inventory | Intégrée à `main` |
| 8 | Transferts / FEFO | Intégrée à `main` |
| 9 | POS ↔ Stock | Intégrée à `main` |
| 10 | SaaS Billing | Intégrée à `main` |
| 11 | Business Intelligence | Intégrée à `main` |
| 12 | Consolidation qualité | En cours |

## Méthode de validation

La CI reste un contrôle utile, mais elle ne doit pas bloquer le projet pour des erreurs non fonctionnelles de formatage ou d'outillage. Chaque phase doit au minimum faire l'objet d'une revue du diff, de tests métier ciblés et d'un contrôle de sécurité/régression avant fusion.
