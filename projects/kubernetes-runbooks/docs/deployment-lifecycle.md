# Déploiements et changements

Un ConfigMap modifié n'implique pas une configuration rechargée. Une variable
d'environnement reste celle du démarrage du processus. Un fichier monté peut
changer mais le logiciel doit savoir le recharger ; un montage `subPath` a
des contraintes spécifiques.

Pour une mise à jour : valider artefact et checksum, conserver la version
précédente, définir les contrôles et suivre `rollout status`. Lire événements
et probes après le rollout, puis exécuter le parcours fonctionnel.

Un patch de fichier à chaud dans un pod est temporaire et peut disparaître
au prochain remplacement. Documenter cette limite et reporter le correctif
dans l'image ou la configuration versionnée. Un pod Terminating doit être
analysé : finalizers, état du nœud, volumes et arrêt applicatif. Ne pas retirer
un finalizer ou forcer la suppression sans comprendre le contrôleur concerné.
