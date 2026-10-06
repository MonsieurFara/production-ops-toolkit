# Import Metricbeat / Kibana

Pour une erreur d'import, noter versions de Beat/Kibana, statut HTTP et fichier
précis. Vérifier disponibilité et privilèges avant de relancer l'import.
Un timeout HTTP 503 ne prouve pas une incompatibilité de chaque dashboard.
Conserver les saved objects avant toute opération de remplacement.

Un contournement ciblé sur un dashboard vSphere doit être documenté et
retiré après correction. Éviter un déplacement global des fichiers fournis
par l'agent. Les spécifications Vega de cette collection utilisent le contexte
du dashboard sans `body.query` additionnelle, afin d'éviter leur conflit.
