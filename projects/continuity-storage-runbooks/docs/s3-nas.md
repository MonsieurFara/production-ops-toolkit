# S3 / MinIO / NAS

Séparer stockage objet, filesystem, métadonnées de l'application et index.
Inventorier objets et versions, rétention, politiques, chiffrement, capacité
et dépendances. Un nombre d'objets ou un volume identique ne prouve pas la
cohérence du contenu. Un miroir additif ne retire pas les anciens objets cible
et ne met pas nécessairement à jour un objet déjà présent.

Pour un filesystem : comparer tailles puis SHA-256 sur un périmètre défini.
Pour S3 : vérifier comportement de versioning, multipart, métadonnées et
méthode de checksum ; l'ETag n'est pas un SHA-256 universel.

Les exports d'alias MinIO peuvent contenir des clés. Les transmettre par un
canal protégé et les garder hors des dépôts. Les commandes destructives de
synchronisation demandent un plan distinct, une sauvegarde et un aperçu validé.
