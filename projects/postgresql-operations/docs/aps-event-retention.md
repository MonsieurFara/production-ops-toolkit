# Événements APS et rétention

Une croissance de `act_evt_log` doit être analysée avec la génération, le
traitement, l'indexation et les besoins de conservation métier. Vérifier les
paramètres effectivement chargés, les consommateurs et l'état Elasticsearch.
Commencer par la taille de relation et les statistiques estimées ; un COUNT
complet d'une très grande table peut être coûteux.

Ne pas conclure qu'un paramètre a pris effet uniquement parce qu'un ConfigMap
a changé. Distinguer nouveaux événements, backlog existant, événements traités
et erreurs de traitement. Préparer sauvegarde et plan de rétention avant
toute purge. Cette collection ne contient pas de suppression automatique.

Un verrou Liquibase ne se libère qu'après vérification de l'absence d'une
migration active, de la sauvegarde et de la cohérence du changelog.
