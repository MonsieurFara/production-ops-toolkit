# Valider une restauration

1. Restaurer dans un environnement isolé à partir d'une sauvegarde identifiée.
2. Contrôler checksum, version, fichiers, schéma et contraintes.
3. Vérifier cohérence entre objets/documentation et métadonnées applicatives.
4. Exécuter des parcours métier fictifs, observer logs et erreurs.
5. Mesurer le point des données, le temps de reprise et les écarts.
6. Conserver le compte rendu et corriger la procédure avant nouvel exercice.

Une table des matières `pg_restore --list` lisible est un contrôle de forme ;
elle ne remplace pas une restauration. Une réplication saine ne protège pas
d'une suppression répliquée. Conserver plusieurs points de restauration.
