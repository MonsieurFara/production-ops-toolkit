> Projet de la [collection technique](../../README.md). Exécuter les commandes de ce guide depuis ce dossier. La validation continue est pilotée par le workflow à la racine de la collection.

# Continuité et stockage

Contrôle d'intégrité local, plan de synchronisation S3 et procédures de reprise.
Les outils publics sont reconstruits ; aucune topologie, capacité réelle,
identité de bucket ni donnée d'entreprise n'est incluse.

```bash
python3 scripts/integrity_manifest.py create examples/data --output artifacts/manifest.json
python3 scripts/integrity_manifest.py verify examples/data --manifest artifacts/manifest.json
python3 scripts/mirror_plan.py --source lab-source/demo --target lab-target/demo
python3 -m unittest discover -s tests -v
```

Le plan `mc mirror` ne s'exécute que avec `--execute`. Il ne contient aucune
option de suppression ou d'écrasement. Les alias et leurs identifiants doivent
être configurés hors Git. Un miroir ne remplace pas une sauvegarde versionnée.

Voir [la préparation PCA/PRA](docs/pca-pra.md), [le stockage S3/NAS](docs/s3-nas.md)
et [la validation de restauration](docs/restore-validation.md).
Tests locaux d'intégrité et du plan ; aucune synchronisation distante exécutée.
