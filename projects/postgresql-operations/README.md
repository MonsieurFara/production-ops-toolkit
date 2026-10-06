> Projet de la [collection technique](../../README.md). Exécuter les commandes de ce guide depuis ce dossier. La validation continue est pilotée par le workflow à la racine de la collection.

# PostgreSQL Operations — PostgreSQL 16/17

Catalogue de diagnostics, sauvegarde et préparation d'une réplication logique.
Les requêtes système sont reconstruites et les requêtes applicatives sont
des exemples à confronter au schéma réel. Aucun secret de connexion n'est inclus.

## Utiliser une connexion protégée

Définir un service libpq dans un fichier privé `pg_service.conf`, puis fournir
les identifiants par `.pgpass` protégé ou par votre gestionnaire de secrets.

```bash
PGSERVICE=lab psql -X -v ON_ERROR_STOP=1 -f sql/01_database_sizes.sql
PGSERVICE=lab bash scripts/backup_database.sh artifacts
PGSERVICE=lab bash scripts/backup_database.sh artifacts --schema-only
```

| Ensemble | Contenu |
|---|---|
| `sql/01…06` | Tailles, activité, blocages, maintenance, connexions et index invalides |
| `sql/07…12` | Émetteur/récepteur, slots, abonnements, tables synchronisées et publications |
| `sql/13…16` | Séquences, identité de réplication, SSL et privilèges |
| `sql/17…18` | Inventaire du schéma et diagnostic d'un verrou Liquibase |
| `application/` | Exemples Activiti, licences ACS et comptes Liferay |
| `docs/` | Migration, séquences, PgBouncer, Patroni et traitement des événements APS |

La collecte peut révéler des requêtes et identifiants internes. Garder les
résultats hors Git. Prérequis : `psql`, `pg_dump` et `pg_restore` adaptés à la
version du serveur ; les vues de statistiques peuvent exiger `pg_read_all_stats`.

## Validation

Syntaxes des scripts vérifiées ; SQL relu et contrôlé par analyse statique.
Aucun serveur PostgreSQL n'était disponible pour exécuter les requêtes dans
la session de préparation. Les scripts de changement restent des procédures
à appliquer après validation en laboratoire.
