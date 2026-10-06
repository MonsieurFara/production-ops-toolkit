# Release GitOps

Séparer dépôt applicatif, artefact d'image et manifests de déploiement.
Conserver commit, version, checksum/digest et ordre des migrations. Vérifier
la synchronisation Argo CD avec l'état réel du cluster puis le parcours métier.

Ordre indicatif à valider selon le système : données, stockage, identité,
configuration, services, gateway, front et observabilité. Un Job de migration
en erreur ne doit pas être masqué par une simple relance du deployment.

Les secrets sont injectés par une solution adaptée à l'environnement. Un
ConfigMap n'est pas un coffre. Documenter le retour arrière des données ;
revenir à une ancienne image ne revient pas automatiquement à un ancien schéma.
