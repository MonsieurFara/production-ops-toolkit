# Contribuer

Décrire le problème, l'environnement de laboratoire et le résultat attendu.
Ajouter un exemple synthétique reproductible. À la racine, lancer
`python3 tools/validate_collection.py`. Dans un projet autonome, lancer
`python3 tools/validate.py` et les tests présents avant de proposer une modification.

Les changements d'exploitation doivent préciser préconditions, sauvegarde,
effet attendu, vérification et retour arrière. Le code adapté d'un ancien
script doit conserver sa provenance et ses limites dans `PROVENANCE.md`.

## Inventaire de publication

Après une modification des fichiers, actualiser l'inventaire avec
`python3 tools/inventory.py --write`, puis vérifier
`python3 tools/inventory.py --check` avant publication.

