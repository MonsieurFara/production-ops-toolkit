# Sauvegarde MongoDB avant chargement

Préparer une sauvegarde et un exercice de restauration isolé. Utiliser un
fichier privé pour les paramètres sensibles plutôt qu'un mot de passe dans
une URI de ligne de commande.

```bash
# MONGO_PRIVATE_CONFIG désigne un fichier YAML protégé hors du dépôt.
mongodump --config "$MONGO_PRIVATE_CONFIG" --archive=artifacts/organigramme.archive --gzip
```

Pour la restauration, identifier la base cible, les namespaces, les options
de remplacement et les versions des Database Tools avant de lancer
`mongorestore`. La restauration API fonctionnelle d'unités peut recréer des
IDs ; elle ne remplace pas une sauvegarde de base testée.

Source : https://www.mongodb.com/docs/database-tools/mongodump/
