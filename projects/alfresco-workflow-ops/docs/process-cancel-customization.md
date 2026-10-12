# Personnaliser la fenêtre d'annulation APS

## Provenance et portée

Le fichier [récupéré](../recovered/process-cancel.html) reproduit exactement
le contenu HTML d'un bloc heredoc retrouvé dans une conversation de mai 2026.
Il conserve le contrôleur `CancelProcessCtrl` et un bouton « Close Window »
qui appelle `cancel()`. Le contrôleur JavaScript et le backend n'ont pas été
récupérés : ce libellé ne prouve donc pas que le bouton ferme seulement la
fenêtre ou que l'annulation d'un processus est interdite.

La [variante de fermeture](../examples/process-cancel-close-only.html) est
une adaptation nouvelle : elle remplace cet appel par `$hide()`, déjà utilisé
par la croix de fermeture dans le HTML retrouvé. Elle doit être vérifiée avec
la version réelle d'APS et sa bibliothèque de modales. Elle change l'interface ;
une interdiction d'annulation doit aussi être appliquée et testée côté API,
permissions et backend. Masquer un bouton ne constitue pas un contrôle d'accès.

Les commandes suivantes sont des exemples reconstruits, paramétrés et
anonymisés. Aucun déploiement réel ni résultat de production n'est attesté
par cette publication.

## Préparer un montage ConfigMap durable

Le [générateur de plan](../scripts/plan_process_cancel_patch.py) lit la
variante `examples/process-cancel-close-only.html` et crée deux fichiers JSON
dans un **nouveau** dossier. Il ne contacte pas Kubernetes et ne déploie rien.
Depuis la racine de la collection :

```bash
set -eu
NS=ops-lab
DEPLOY=workflow-app
CONTAINER=workflow-app
CONFIGMAP=process-cancel-ui-v1
PLAN_PARENT="$(mktemp -d)"
PLAN_DIR="$PLAN_PARENT/plan"

python3 projects/alfresco-workflow-ops/scripts/plan_process_cancel_patch.py \
  --namespace "$NS" --deployment "$DEPLOY" --container "$CONTAINER" \
  --configmap "$CONFIGMAP" --output "$PLAN_DIR"
```

Le plan contient `configmap.json` et `deployment-patch.json`. Le second est
un patch **strategic merge**, pas un Deployment complet : ne pas l'appliquer
avec `kubectl apply`. Le chemin de montage par défaut est le chemin Tomcat
documenté ici ; `--mount-path` permet de fournir un chemin POSIX absolu et
normalisé différent, après vérification de l'image.

Relire le plan et comparer le nom du conteneur, les volumes et les montages
au Deployment existant. Le patch ne vérifie pas leur existence dans un
cluster ; un nom de conteneur erroné peut ajouter une entrée invalide.
Vérifier également l'absence de conflit avec un montage existant au même
chemin ou un volume nommé `process-cancel-ui`.

Après revue, dans l'environnement autorisé, créer d'abord la ConfigMap puis
appliquer le patch :

```bash
kubectl apply -f "$PLAN_DIR/configmap.json"
kubectl patch deployment "$DEPLOY" -n "$NS" \
  --type strategic --patch-file "$PLAN_DIR/deployment-patch.json"
kubectl rollout status deployment/"$DEPLOY" -n "$NS" --timeout=180s
```

Le fichier est monté en lecture seule avec `subPath`. La personnalisation
est alors conservée à la recréation des pods tant que la ConfigMap et le
Deployment restent disponibles. L'annotation du template contient le SHA-256
du HTML : un plan régénéré à partir d'un contenu modifié change cette
annotation et déclenche un rollout. Une modification manuelle de la ConfigMap
seule ne met pas à jour un montage `subPath` déjà présent, conformément à la
[documentation des ConfigMaps Kubernetes](https://kubernetes.io/docs/concepts/configuration/configmap/).

Versionner les manifests validés dans la source de vérité du déploiement,
avec des noms de ConfigMap distincts pour les versions à conserver. Garder
l'ancienne ConfigMap et le manifeste antérieur permet un retour explicite à
la version précédente. Un simple `rollout undo` ne restaure pas les données
d'une ConfigMap qui aurait été écrasée sous le même nom.

Effectuer les contrôles fonctionnels décrits plus bas après le rollout.
Ce montage ne crée aucune règle d'autorisation côté backend.

## Préparer un essai à chaud

Exécuter depuis la racine de la collection, dans un environnement de test
autorisé. Le conteneur doit permettre l'écriture du fichier déployé.
Cette méthode est une alternative temporaire au montage ConfigMap ; ne pas
l'utiliser sur le fichier monté en lecture seule décrit ci-dessus.

```bash
set -eu
NS=workflow-lab
DEPLOY=workflow-app
SELECTOR='app=workflow-app'
CONTAINER=workflow-app
TARGET=/usr/local/tomcat/webapps/activiti-app/workflow/views/modal/process-cancel.html
SOURCE=projects/alfresco-workflow-ops/examples/process-cancel-close-only.html

kubectl get deployment "$DEPLOY" -n "$NS"
POD="$(python3 projects/kubernetes-runbooks/scripts/ready_pod.py \
  --namespace "$NS" --selector "$SELECTOR")"
test -f "$SOURCE"
kubectl exec -n "$NS" "$POD" -c "$CONTAINER" -- test -f "$TARGET"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="${TARGET}.bak.${STAMP}"
kubectl exec -n "$NS" "$POD" -c "$CONTAINER" -- cp -p "$TARGET" "$BACKUP"
printf 'Sauvegarde dans le pod %s : %s\n' "$POD" "$BACKUP"
```

Le [sélecteur de pod](../../kubernetes-runbooks/scripts/ready_pod.py) exige
exactement un pod Running et Ready et exclut les pods en suppression.
Adapter le label au composant applicatif, pour exclure l'administration.
Avec plusieurs réplicas prêts, il refuse la sélection ; prévoir alors un
déploiement cohérent de tous les réplicas.

Après la sauvegarde, écrire la variante dans ce même pod :

```bash
kubectl exec -i -n "$NS" "$POD" -c "$CONTAINER" \
  -- sh -c 'cat > "$1"' sh "$TARGET" < "$SOURCE"

kubectl exec -n "$NS" "$POD" -c "$CONTAINER" -- cat "$TARGET"
```

Cette commande écrase le fichier ; une interruption peut laisser une copie
incomplète. Le retour arrière ci-dessous réutilise la sauvegarde. Ne pas lancer
cet essai sur un système de fichiers en lecture seule, un fichier géré par un
volume projeté ou un chemin qui diffère de celui vérifié.

## Vérifier et revenir en arrière

Recharger le navigateur en vidant son cache. Vérifier la croix, le bouton
« Close Window », l'absence de requête d'annulation au clic et le statut du
processus après fermeture. Vérifier également le comportement des API
d'annulation avec les comptes concernés, indépendamment de l'interface.

Ne pas conclure à une interdiction backend sur la seule présence des textes
dans le fichier. Selon la version, le serveur ou le navigateur peut conserver
une ressource en cache ; constater son comportement au lieu de supposer
qu'une édition du fichier suffit.

Pour restaurer, dans la même session et tant que ce pod et sa sauvegarde
existent :

```bash
kubectl exec -n "$NS" "$POD" -c "$CONTAINER" -- cp -p "$BACKUP" "$TARGET"
```

Une modification dans le système de fichiers du conteneur peut disparaître
à la recréation du pod. Un redémarrage n'est pas une méthode de persistance.
Après validation, intégrer la personnalisation à l'image ou au mécanisme
de déploiement compatible avec APS, versionner le changement et effectuer
un rollout contrôlé. Conserver un artefact antérieur pour le retour arrière.

