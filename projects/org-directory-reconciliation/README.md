> Projet de la [collection technique](../../README.md). Exécuter les commandes de ce guide depuis ce dossier. La validation continue est pilotée par le workflow à la racine de la collection.

# Organigramme / Directory Reconciliation

Préparation et rapprochement de référentiels RH/annuaire avec conservation
de l'identité d'autorité. Quatre scripts JavaScript ont été retrouvés dans les
sources. Leur version publique est adaptée : commentaires internes retirés,
cibles anonymisées, secrets par variables de processus et timeout réseau.

## Laboratoire hors ligne

```bash
python3 scripts/reconcile.py --source examples/hr.csv --target examples/directory.csv --output artifacts/plan.json
node recovered/build_seed_from_personnel.js examples/personnel.csv artifacts/seed.json
python3 -m unittest discover -s tests -v
```

| Fichier | État et effet |
|---|---|
| `scripts/reconcile.py` | Nouvelle reconstruction ; plan local, sans création ni appel d'API |
| `recovered/build_seed_from_personnel.js` | Script retrouvé et adapté ; produit un seed et un module JS local |
| `recovered/seed_organigramme_api.js` | Script retrouvé et adapté ; simulation par défaut, API métier spécifique à vérifier |
| `recovered/restaurer_organigramme.js` | Script retrouvé et adapté ; restauration fonctionnelle, simulation par défaut |
| `recovered/supprimer_doublons_employes.js` | Script retrouvé et adapté ; opérations de suppression uniquement en exécution explicite |

Lancer les scripts `recovered/` depuis leur dossier et lire [les limites du
contrat API](docs/recovered-scripts.md). Les identifiants sont fournis par
`ORG_API_URL`, `ORG_API_USER`, `ORG_API_PASSWORD`, jamais par mot de passe dans
la ligne de commande. Aucun export RH réel, seed original ou dump n'est fourni.

## Invariants

Le rapprochement hors ligne conserve le nom, l'email, l'ID et le lien Keycloak
de la cible. Il ne propose que `unit_code` et `job_title`. Les doublons ou
identités incohérentes sont signalés ; les absents ne sont pas créés.

Tests sur données synthétiques : ambiguïtés, identités conservées, nouveaux
comptes exclus et génération du seed. Les mutations via l'API historique ne
sont pas validées contre un service réel dans cette collection.
