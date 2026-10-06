> Projet de la [collection technique](../../README.md). Exécuter les commandes de ce guide depuis ce dossier. La validation continue est pilotée par le workflow à la racine de la collection.

# Kubernetes Runbooks

Procédures et outils de diagnostic issus de sujets d'exploitation de
plateformes conteneurisées. Les sélecteurs, namespaces et ressources de la
collection sont des paramètres ou des exemples de laboratoire.

## Démarrage

```bash
python3 scripts/ready_pod.py --namespace lab --selector app=demo
python3 scripts/cluster_snapshot.py --namespace lab --output artifacts/snapshot.json
python3 -m unittest discover -s tests -v
```

`ready_pod.py` refuse une sélection vide ou ambiguë. Il exclut les pods en
suppression, hors phase Running ou dont un conteneur n'est pas prêt.
`cluster_snapshot.py` conserve un sous-ensemble de l'état, sans environnement
des conteneurs, Secret, ConfigMap ni logs applicatifs.

| Runbook | Objet |
|---|---|
| [Pression mémoire](docs/memory-pressure.md) | Distinguer Evicted, OOMKilled, requests/limits et capacité du nœud |
| [Réseau et dépendances](docs/network-and-dependencies.md) | DNS, Service, endpoints, TCP/gRPC, Ingress et CORS |
| [Registres containerd](docs/containerd-registries.md) | Certificats, hosts.toml, registre HTTP de laboratoire et image absente |
| [Déploiement et opérations](docs/deployment-lifecycle.md) | Rollout, probes, arrêt propre, pods Terminating et changements de configuration |

Les manifests sont des exemples à adapter ; aucun manifeste n'est appliqué
automatiquement. Tests locaux sur sélection de pods simulés et parsing des
quantités mémoire. Les appels kubectl nécessitent un cluster de laboratoire.
