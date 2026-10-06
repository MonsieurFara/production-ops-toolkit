# Documents présents dans ACS, contrôle APS négatif

Cas adapté d'une procédure de dépannage retrouvée. Le fichier interne d'origine
reste hors de cette collection ; les paramètres ci-dessous sont génériques.

| Composant | Contrôle |
|---|---|
| Repository ACS | Accès Nodes et métadonnées ; existence et permissions des pièces |
| ContentStore | Lecture du contenu ; séparer existence et intégrité |
| Solr / ModelTracker | NamespaceException, collision de modèle, progression des trackers |
| CMIS | IN_FOLDER pour un dossier ; IN_TREE pour l'arborescence |
| APS | Rejouer le contrôle documentaire avec l'identité applicative correcte |

Dans le cas retrouvé, un ancien modèle personnalisé dans le cache Solr
provoquait une collision de namespace. Sa mise en quarantaine, suivie d'un
redémarrage contrôlé de Solr, a permis la régénération du modèle et le retour
des résultats CMIS. Cette cause doit être démontrée avant d'appliquer la procédure.

## Séquence

1. Confirmer existence des documents et droits de l'identité utilisée par APS.
2. Comparer les recherches de même portée et noter la pagination.
3. Examiner ModelTracker et identifier **un fichier précis** obsolète.
4. Vérifier sauvegarde et persistance du volume, puis préparer la quarantaine.
5. Redémarrer le deployment, attendre le readiness et récupérer le nouveau pod.
6. Contrôler disparition de la collision et reprise d'indexation.
7. Valider CMIS, lecture des pièces et parcours APS avant clôture.

Le retour arrière remet le fichier sauvegardé uniquement si le diagnostic est
invalidé ; vérifier les autres modèles avant redémarrage. Ne pas supprimer
l'ensemble des index. Les queues de transformation ActiveMQ constituent une
piste distincte et ne prouvent pas une erreur de recherche documentaire.
