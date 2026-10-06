> Projet de la [collection technique](../../README.md). Exécuter les commandes de ce guide depuis ce dossier. La validation continue est pilotée par le workflow à la racine de la collection.

# Delivery / Change Management

Modèles et outils pour préparer une mise en production, relire l'exploitabilité,
contrôler un artefact et documenter la validation. Les exemples sont fictifs ;
les dossiers et approbations internes ne sont pas redistribués.

```bash
python3 scripts/validate_release.py examples/release.json
python3 -m unittest discover -s tests -v
# Générateur de notes ITIL adapté d'un fichier retrouvé (dépendance optionnelle) :
python3 scripts/generate_itil_notes.py --output output/itil-notes.docx
```

| Ressource | Utilité |
|---|---|
| `templates/change.md` | Besoin, périmètre, fenêtres, validation et retour arrière |
| `templates/acceptance.md` | Recette technique et fonctionnelle avec preuves |
| `templates/incident.md` | Chronologie, hypothèses, cause confirmée et actions |
| `templates/maintenance.md` | Anomalie, effet métier et correction proposée |
| `templates/daily-report.md` | Compte rendu quotidien concis |
| `templates/weekly-report.md` | Synthèse de période et décisions attendues |
| `cases/` | Cas anonymisés : KYC, IAM, workflows, EHR, services documentaires et impression |
| `docs/` | GitOps, exploitabilité, ITIL et documentation |

Le validateur vérifie le manifeste et le checksum des fichiers ; il ne déploie
rien et ne remplace pas la recette métier. Tests sur intégrité d'artefact et
contrats du manifeste. Le générateur ITIL est adapté d'un script retrouvé.
