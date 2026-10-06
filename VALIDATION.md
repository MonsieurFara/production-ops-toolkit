# Validation de la collection

Date : 6 octobre 2026.

**44 tests fonctionnels locaux réussis**, dans huit projets comportant des tests.
Le projet PostgreSQL est contrôlé statiquement ; aucun serveur n'a été utilisé.

| Projet | Tests locaux |
|---|---:|
| production-ops-toolkit | 8 |
| kubernetes-runbooks | 6 |
| alfresco-workflow-ops | 6 |
| iam-sso-operations | 2 |
| observability-dashboards | 8 |
| continuity-storage-runbooks | 5 |
| delivery-change-management | 4 |
| org-directory-reconciliation | 5 |

Les syntaxes Python, JavaScript, Bash et JSON ont été contrôlées.
Le calcul des KPI et le dashboard HTML ont été exécutés sur données synthétiques.
Le générateur de notes ITIL a produit un DOCX temporaire lors de la préparation.

La validation GitHub Actions est configurée. Son résultat effectif doit être
consulté dans l'onglet Actions ; un résultat local n'atteste pas une exécution CI.

Aucun cluster Kubernetes, AD, serveur PostgreSQL, service ACS/APS, Grafana,
Kibana, MinIO ni workspace Sentinel de production n'a servi aux tests.
Les imports de dashboards, SQL, règles et scripts dépendant de ces plateformes
nécessitent encore un laboratoire. Les clients API historiques ont un contrat
à vérifier avant utilisation.
