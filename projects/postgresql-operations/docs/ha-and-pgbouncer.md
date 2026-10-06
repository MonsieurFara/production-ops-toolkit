# Haute disponibilité, Patroni et PgBouncer

Séparer le service PostgreSQL, le gestionnaire de HA et le pooler. Identifier
le primaire à partir de l'état du gestionnaire et de `pg_is_in_recovery()`.
Un serveur PostgreSQL actif ne prouve pas que Patroni gère son cycle de vie.
Ne pas démarrer simultanément le service direct et Patroni sur le même PGDATA.

Dans la console administrative PgBouncer, les commandes de lecture utiles sont
`SHOW POOLS;`, `SHOW STATS;`, `SHOW DATABASES;` et `SHOW CLIENTS;`.
Leurs sorties sont privées. Vérifier les modes session/transaction et les
besoins des pilotes avant de modifier le routage applicatif.

Pour un incident SSL ou c3p0 : vérifier la configuration effectivement chargée,
le driver, les temps TCP/TLS, la saturation du pool et le coût des requêtes.
La latence TCP seule ne suffit pas à expliquer un temps applicatif élevé.
