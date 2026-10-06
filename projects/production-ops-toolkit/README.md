> Projet de la [collection technique](../../README.md). Exécuter les commandes de ce guide depuis ce dossier. La validation continue est pilotée par le workflow à la racine de la collection.

# Production Ops Toolkit

Outils portables pour diagnostiquer un incident et conserver une preuve locale.
Version publique reconstruite à partir de sujets d'exploitation Linux et applicative.

| Outil | Usage | Effet |
|---|---|---|
| `scripts/collect_linux.sh` | Ressources, services défaillants et sockets | Lecture locale ; écrit un dossier de collecte protégé |
| `scripts/http_probe.py` | Code HTTP, latence et en-têtes CORS | Une requête vers l'URL donnée ; aucun corps de réponse affiché |
| `scripts/tls_probe.py` | Chaîne de confiance et certificat | Une connexion TLS avec validation du certificat |
| `scripts/trace_logs.py` | Recherche littérale d'identifiants | Lecture locale ; compte les correspondances par défaut |

## Démarrage

```bash
bash scripts/collect_linux.sh artifacts
python3 scripts/http_probe.py https://example.com/health --origin https://portal.example.com
python3 scripts/tls_probe.py example.com --port 443
python3 scripts/trace_logs.py --id DEMO-TX-001 --files examples/application.log.example
python3 -m unittest discover -s tests -v
```

Prérequis : Python 3.12, Bash et utilitaires Linux. Les probes ne parcourent
aucun réseau ; chaque cible doit être fournie explicitement.

`--show-lines` active l'affichage des lignes de logs. Elles peuvent contenir
des données métier malgré le masquage de motifs courants. Les collectes ne
doivent pas être ajoutées à Git. Voir [les méthodes d'investigation](docs/incident-triage.md).

## Validation et limites

Tests locaux sur serveur HTTP simulé et journaux synthétiques ; syntaxe Bash
vérifiée. Aucun test sur une infrastructure d'entreprise dans cette collection.
