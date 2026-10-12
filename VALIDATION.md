# Validation de la collection

Date : 12 octobre 2026.

Le jeu comprend **53 tests fonctionnels**, dans huit projets comportant des tests.
Le projet PostgreSQL est contrôlé statiquement ; aucun serveur n'a été utilisé.

| Projet | Tests |
|---|---:|
| production-ops-toolkit | 8 |
| kubernetes-runbooks | 6 |
| alfresco-workflow-ops | 11 |
| iam-sso-operations | 2 |
| observability-dashboards | 8 |
| continuity-storage-runbooks | 5 |
| delivery-change-management | 8 |
| org-directory-reconciliation | 5 |

Les 44 tests de la publication initiale ont réussi sous Linux le 6 octobre,
avec les contrôles Bash, Python, JavaScript et JSON. Le calcul des KPI, le
dashboard HTML et un DOCX ITIL temporaire ont été vérifiés lors de cette préparation.

La reprise ajoute quatre tests du validateur de release et cinq tests du
générateur ConfigMap / patch Deployment. Les 8 tests Delivery et les 11 tests
Alfresco réussissent localement. Le générateur produit les deux documents
JSON attendus ; aucun kubectl n'est lancé par celui-ci.

Sur le poste Windows de la reprise, quatre tests historiques ne peuvent pas
aboutir : trois nécessitent un socket HTTP local bloqué par le bac à sable,
et un nécessite le privilège de création de lien symbolique. Le runtime Bash
est également indisponible dans ce bac à sable. Ces contraintes ne valent pas
réussite des contrôles ; le workflow Linux reprend la totalité des 53 tests
et des contrôles de syntaxe.

La [validation GitHub Actions initiale](https://github.com/MonsieurFara/production-ops-toolkit/actions/runs/37508812655)
est réussie. Pour chaque nouvelle révision, consulter son résultat dans
[l'onglet Actions](https://github.com/MonsieurFara/production-ops-toolkit/actions).
Un résultat local n'atteste pas une exécution CI. Le workflow vérifie aussi
l'inventaire SHA-256. Les manifests JSON sont décodés et le plan est testé ;
les fichiers YAML historiques ne sont pas soumis à un validateur de schéma Kubernetes.

Aucun cluster Kubernetes, AD, serveur PostgreSQL, service ACS/APS, Grafana,
Kibana, MinIO ni workspace Sentinel de production n'a servi aux tests.
Les imports de dashboards, SQL, règles et scripts dépendant de ces plateformes
nécessitent encore un laboratoire. Les clients API historiques ont un contrat
à vérifier avant utilisation.
