# Pression mémoire

| Signal | Diagnostic |
|---|---|
| Pod Evicted | Lire motif et événement kubelet ; vérifier pression du nœud et seuil d'éviction |
| Container OOMKilled | Vérifier limite mémoire, heap JVM, mémoire native et historique |
| Pod Pending | Lire FailedScheduling : ressources, affinités, taints, PVC ou quota |
| Capacité OS différente de Node.capacity | Vérifier hyperviseur, OS et état du kubelet avant toute intervention |
| Pod Ready mais application lente | Examiner GC, threads, pool DB et dépendances ; la probe seule ne suffit pas |

Collecter `kubectl describe pod`, événements, `kubectl top` si Metrics Server
est disponible, requests/limits et capacité/allouable. Comparer consommation
réelle et réservations. La mémoire physique, allouable et disponible désigne
trois valeurs différentes.

Une modification matérielle peut nécessiter une réconciliation de l'état du
nœud. Planifier cordon/drain et interruption selon les PDB et les volumes ;
un redémarrage du kubelet ne constitue pas une correction automatique universelle.
