# Adaptateurs SQL et index

Les tables système sont interrogées en lecture seule. Les exemples
applicatifs demandent un inventaire du schéma : noms entre guillemets,
types, tenant, clés de jointure et définition des statuts.

L'exemple d'absences utilise `business_absence` et des variables de workflow
génériques. Il illustre l'ajout de l'email avec une jointure explicite. Retirer
une jointure inutilisée évite la multiplication involontaire des lignes ;
`DISTINCT` ne remplace pas l'analyse de la cardinalité et des homonymes.

`index_candidates.sql` propose deux index à évaluer. Ils ne sont pas des
commandes de diagnostic et peuvent consommer I/O, CPU et disque. Vérifier
les index existants et l'effet du plan avant création. La création concurrente
ne se lance pas dans BEGIN/COMMIT ; en cas d'échec, vérifier l'état de l'index.

Une archive gzip lisible et une table des matières cohérente ne prouvent pas
une restauration applicative. Restaurer et tester dans un environnement isolé.
Les exports de rôles, même sans mot de passe, sont des données d'administration
à garder hors Git.
