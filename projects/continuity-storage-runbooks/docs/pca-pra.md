# Préparation PCA/PRA

La reprise couvre application, identité, base, documents, réseau et supervision.
Définir les objectifs RTO/RPO avec les propriétaires métier ; ils ne doivent
pas être remplacés par une disponibilité observée ni par un objectif générique.

| Composant | Dépendance à inventorier | Preuve de reprise |
|---|---|---|
| Portail / applications | DNS, TLS, identité et endpoints | Parcours utilisateur complet |
| IAM / SSO | Annuaire, base, clients et clés | Connexion et contrôle des permissions |
| PostgreSQL | Sauvegarde, WAL, réplication et pooler | Point restauré, intégrité et écritures synthétiques |
| Stockage documents | Objets, métadonnées, versions et politiques | Lecture de documents et rapprochement des références |
| Kubernetes / runtime | Images, manifests, volumes et configurations | Pods prêts et Services accessibles |
| Observabilité | Agents, collecte, dashboards et alertes | Détection d'une anomalie injectée en laboratoire |

Préparer l'ordre de reprise, les responsables, un plan de communication et
des points d'arrêt. Mesurer RTO/RPO à partir d'un exercice daté. Tester aussi
le retour au fonctionnement nominal, notamment la convergence des écritures.
