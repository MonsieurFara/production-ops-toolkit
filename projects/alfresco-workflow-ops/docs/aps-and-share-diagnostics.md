# APS, recherche, Share et interfaces

## APS / Activiti

Séparer état métier, tâches actives et événements techniques. Une tâche en
attente n'est pas nécessairement un échec. Documenter la règle de clôture,
le propriétaire métier et l'identifiant de corrélation avant intervention.
Sur les lenteurs, rapprocher mémoire/GC, connexions PostgreSQL, verrouillages,
timeouts, pools JDBC et dépendances externes.

## Alfresco Share / Aikau

Vérifier présence du JAR, contenu réel de l'archive, version chargée, chemin
de ressource et logs DependencyAggregator. La présence d'une bibliothèque
ne garantit pas l'existence de la ressource JavaScript attendue.

## Licences ACS

Un audit des comptes autorisés et supprimés est une lecture utile. La
révocation doit passer par les fonctions supportées et une revue des comptes
techniques et de la synchronisation LDAP. Ne pas modifier directement
`alf_auth_status` pour contourner le mécanisme de licence.

## Corrections à chaud

Un fichier remplacé dans un pod est éphémère. Conserver checksum, copie de
retour arrière et justification, puis intégrer le correctif dans l'artefact
versionné. Les JAR internes et modèles commerciaux ne sont pas fournis ici.
