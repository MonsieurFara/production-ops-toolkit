# Préparer une migration par réplication logique

1. Inventorier bases, schémas, extensions, rôles, contraintes et séquences.
2. Vérifier version, réseau, TLS, `wal_level`, slots et workers disponibles.
3. Exporter le schéma et le comparer à la cible ; le DDL ne suit pas la réplication.
4. Valider les tables publiées et l'identité de réplication pour UPDATE/DELETE.
5. Créer l'abonnement dans la base cible correspondant à la base de la publication.
6. Suivre copie initiale, état des relations, workers, retards et WAL conservé.
7. Tester des insertions/modifications/suppressions synthétiques autorisées.
8. Préparer arrêt des écritures, synchronisation des séquences et contrôle final.
9. Basculer les connexions après accord du changement ; vérifier l'application.

Une réplication logique n'est pas à elle seule un mécanisme de failover.
La suppression d'un abonnement ou d'un slot peut perdre la position de reprise.
Le retour arrière après de nouvelles écritures cible exige un plan de convergence.

## Séquences

Les valeurs des séquences ne sont pas répliquées. Avant une bascule en écriture,
capturer les valeurs sources dans une fenêtre maîtrisée, comparer les maxima
de données cible et traiter chaque séquence selon incrément, cycle et borne.
Ne pas appliquer un `setval(max(id))` global sur des tables choisies au hasard.

Source : https://www.postgresql.org/docs/17/logical-replication-restrictions.html
