# Revue des accès, signatures et comptes

Pour une suspension/réactivation : disposer d'une liste validée, d'une
référence de changement, de dates et d'une preuve avant/après. Traiter les
exceptions et les retours anticipés avec le responsable habilité. Les motifs
médicaux et informations RH restent hors du dépôt.

Une adresse email seule peut correspondre à un homonyme. Un résultat multiple
doit être arbitré. Conserver un identifiant stable, vérifier l'annuaire source
et documenter la règle de rapprochement avant toute modification.

Pour des comptes Liferay dupliqués, identifier tenant/companyId, compte
historique, email normalisé et dépendances. Utiliser le parcours applicatif
supporté pour corriger, après sauvegarde et contrôle de l'unicité. Les anciens
scripts SQL de modification ne sont pas appliqués automatiquement.

Les statuts SQL doivent être interprétés selon le type et les valeurs réelles :
une colonne `smallint` ne se traite pas avec `UPPER()`. Une valeur numérique
ne doit pas être traduite en ACTIVE/INACTIVE sans définition du schéma.

Les signatures et délégations métier sont des validations séparées des droits
techniques. La revue constate les écarts ; elle ne décide pas du pouvoir de signature.
