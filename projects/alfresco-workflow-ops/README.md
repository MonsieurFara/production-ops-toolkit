> Projet de la [collection technique](../../README.md). Exécuter les commandes de ce guide depuis ce dossier. La validation continue est pilotée par le workflow à la racine de la collection.

# Alfresco / Workflow Operations

Diagnostic de pièces présentes dans ACS mais signalées manquantes dans APS,
contrôles CMIS/Solr et méthodes de suivi Activiti. Le cas documentaire est
adapté d'une procédure retrouvée ; les outils publics sont reconstruits.

## Contrôles

```bash
python3 scripts/compare_documents.py --acs-url https://acs.example.com \
  --cmis-url https://acs.example.com/alfresco/api/-default-/public/cmis/versions/1.1/browser/root \
  --folder 00000000-0000-4000-8000-000000000001 --netrc-file /chemin/prive/acs.netrc
python3 scripts/solr_model_quarantine.py --help
python3 -m unittest discover -s tests -v
```

La comparaison porte sur les **documents directement dans le dossier** :
Nodes children et CMIS `IN_FOLDER`. Pour une arborescence, `IN_TREE` a une
portée différente. Une égalité de compte n'est pas une preuve d'égalité des
documents ou des permissions ; terminer par une vérification fonctionnelle.

`solr_model_quarantine.py` produit un plan par défaut. `--execute` déplace
uniquement le fichier explicitement identifié vers un répertoire de sauvegarde
fourni, puis redémarre le deployment. Le backup doit être sur un volume persistant.

Prérequis : Python 3.12, kubectl pour le runbook Solr et accès de laboratoire.
Tests sur réponses JSON fictives et garde-fous du plan ; aucune correction
appliquée à un service réel pendant la préparation.

## Personnalisation APS récupérée

Le [guide de la modale process-cancel](docs/process-cancel-customization.md)
présente le [HTML historique](recovered/process-cancel.html), ses limites et une
[variante fermant la fenêtre](examples/process-cancel-close-only.html).
Le générateur prépare une ConfigMap et un patch de Deployment, sans contacter
le cluster :

```bash
python3 scripts/plan_process_cancel_patch.py --namespace ops-lab \
  --deployment workflow-app --container workflow-app --output artifacts/process-cancel
```

Des [manifests d'exemple](manifests) sont fournis. Le guide explique leur
adaptation, la validation et le retour arrière. L'autorisation d'annuler un
processus doit être contrôlée côté serveur.
