# Définitions des indicateurs

| KPI | Calcul dans le laboratoire | Limite |
|---|---|---|
| Erreurs serveur | HTTP 5xx / requêtes observées | Les 4xx sont distinguées des erreurs serveur |
| Apdex | (satisfaites + tolérées/2) / total, T=500 ms par défaut | Une réponse HTTP >=400 est frustrée, quelle que soit sa latence |
| p95 | Quantile interpolé des latences observées | Dépend de l'échantillon ; non assimilable à une moyenne |
| MTTD | Moyenne détection - début sur les incidents fournis | Dates avec timezone obligatoires |
| MTTR | Moyenne rétablissement - détection sur les incidents clôturés | Les incidents ouverts sont comptés séparément |
| Clôture de cohorte | Workflows terminés / total unique de la cohorte | Les trois statuts synthétiques sont exclusifs |
| Disponibilité temporelle | À mesurer selon fenêtre, contrôles et exclusions approuvés | Non déduite du seul taux de réussite des requêtes |

Apdex : satisfaite si durée <= T ; tolérée si T < durée <= 4T ; frustrée
au-delà ou en erreur. Une cohorte vide produit une valeur non mesurée.
Préciser période, filtres, couverture et propriétaire de la donnée avant
toute comparaison. Les alertes du laboratoire utilisent des seuils d'exemple.

Pour le suivi métier, normaliser les états via un adaptateur documenté. Ne pas
additionner automatiquement anomalies et en-cours si les catégories réelles
se recouvrent. Définir le dénominateur du dénouement avant de publier le taux.

Source Vega / Kibana : https://www.elastic.co/docs/explore-analyze/visualize/custom-visualizations-with-vega

## Vega et Elasticsearch 8+

Les exemples utilisent `fixed_interval` avec le placeholder Kibana automatique.
Vérifier l'intervalle résolu pour de très longues fenêtres : un intervalle
calendaire comme un mois demande une adaptation explicite. Le champ CPU
normalisé exige la collecte `normalized_percentages`. Appliquer un filtre
`host.name` dans le dashboard pour suivre un hôte précis ; sans filtre, les
valeurs sont une moyenne des échantillons disponibles.
