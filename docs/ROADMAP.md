# Projets en cours de cadrage

| Projet | État confirmé | Travail restant |
|---|---|---|
| Accounting batches indépendant | Idée discutée ; règles comptables et contrats d'entrée/sortie non fournis | Modèle de grand livre, opérations autorisées, contrôle de balance, idempotence, rapprochement et tests métier |
| Plateforme de workflows type APS | Objectif discuté ; application complète non livrée | Modélisation BPMN, moteur, tâches, formulaires, audit, permissions, documents, API et exploitation |
| Portfolio animé | Besoin exprimé ; source complète du site non retrouvée dans les fichiers examinés | Récupérer le projet existant, vérifier AZ-900 et poursuivre la mise au point visuelle |
| Préparation SC-200 | Préparation en cours | Laboratoire Sentinel/Defender, cas pratiques KQL et quiz d'entraînement originaux |
| Cartographie d'infrastructure optique | Deux fichiers HTML de cartographie retrouvés | Publier un exemple à coordonnées fictives ; les localisations réelles restent hors de la collection publique |
| Gouvernance des risques | Travail de cadrage autour d'un outil tiers discuté | Vérifier le déploiement, les licences et les preuves de fonctionnement avant de revendiquer un résultat final |

## Accounting batches — premier périmètre possible

Un laboratoire peut recevoir un fichier d'opérations fictives, vérifier la
balance débit/crédit, conserver une clé d'idempotence, enregistrer les rejets
et produire un rapprochement. Cette proposition n'est pas un moteur comptable
prêt pour un établissement financier. Les règles comptables doivent être
définies avant toute intégration à un système réel.

## Plateforme de workflows — jalons

1. Définir les contrats API, les permissions et l'historique d'audit.
2. Construire un parcours de demande, affectation, décision et clôture.
3. Ajouter formulaires, documents, relances et observabilité.
4. Valider isolation des tenants, reprise, sauvegarde et tests de charge.
5. Choisir le moteur BPMN et vérifier sa licence avant extension.
