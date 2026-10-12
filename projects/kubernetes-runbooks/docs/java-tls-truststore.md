# Java : diagnostiquer HTTPS et monter un truststore

## Provenance

Ce guide est une adaptation anonymisée de commandes et de diagnostics
retrouvés dans une conversation d'août 2026. Les extraits accessibles et leurs
pièces jointes décrivent successivement une connexion HTTP vers un port TLS
et une erreur Java de correspondance entre une IP dans l'URL et le certificat.
Ils montrent aussi l'usage d'un truststore monté dans Kubernetes.

Les journaux, adresses internes et identifiants d'application ne sont pas
publiés. Aucun script MongoDB ni source du déploiement n'a été retrouvé dans
les échanges accessibles. Les dernières instructions de correction n'ont pas
de résultat d'exécution attesté ; ce runbook ne revendique pas de succès
en production.

## Séparer les causes

- HTTP envoyé à un port HTTPS peut provoquer une fermeture avant réponse.
  Une fermeture seule ne prouve pas cette cause : confirmer le protocole.
- Une erreur `PKIX path building failed` peut indiquer une chaîne de
  confiance absente ou incomplète. Vérifier aussi la chaîne servie, la validité
  et le truststore réellement utilisé.
- Une erreur `No subject alternative names matching IP address` indique
  que l'IP utilisée dans l'URL n'est pas couverte par un SAN IP du certificat.
  Ajouter la CA au truststore ne corrige pas ce défaut d'identité.
- Une réponse HTTP 401 obtenue après une négociation TLS réussie relève
  ensuite de l'authentification ou de l'autorisation ; son analyse est distincte.

Conserver un hostname couvert par les SAN DNS du certificat dans l'URL HTTPS.
Le SNI indique au serveur le nom demandé ; la validation SAN vérifie l'identité
présentée. Une résolution vers une IP fixe ne remplace pas ces contrôles.
Ne pas désactiver la validation TLS, le contrôle du hostname ou installer un
gestionnaire `trustAll`.

## Vérifier la dépendance TLS

Exemples Bash à adapter, depuis un poste ayant accès à la dépendance.
Le fichier CA doit provenir d'une source de confiance ; contrôler son empreinte
par un canal indépendant avant l'import.

```bash
set -eu
NS=application-lab
DEPLOY=application
SELECTOR='app=application'
CONTAINER=application
HOST=api.example.com
ADDRESS=192.0.2.10
PORT=8443
CA_FILE=/chemin/prive/org-root-ca.pem

openssl x509 -in "$CA_FILE" -noout -subject -issuer -dates -fingerprint -sha256
openssl s_client -connect "$ADDRESS:$PORT" -servername "$HOST" \
  -verify_hostname "$HOST" -verify_return_error -CAfile "$CA_FILE" </dev/null
```

Ce test contrôle la chaîne et le nom avec OpenSSL et ce fichier CA. Il ne
prouve pas que la JVM utilise la même source de confiance. Une négociation
réussie ne prouve pas non plus le bon fonctionnement de l'appel applicatif.
Pour un certificat serveur public, utiliser les autorités de confiance
appropriées au lieu d'importer un certificat récupéré sans vérification.

Depuis la racine de cette collection, sélectionner le pod prêt puis contrôler
la résolution effective :

```bash
POD="$(python3 projects/kubernetes-runbooks/scripts/ready_pod.py \
  --namespace "$NS" --selector "$SELECTOR")"
kubectl exec -n "$NS" "$POD" -c "$CONTAINER" -- getent hosts "$HOST"
```

[ready_pod.py](../scripts/ready_pod.py) refuse une sélection vide ou ambiguë.
Si l'image ne contient pas `getent`, utiliser un moyen de diagnostic adapté
à cette image ou un conteneur de diagnostic autorisé.

## Construire puis distribuer le truststore

Préférer une image reproductible contenant les CA validées ou un truststore
construit séparément puis monté en lecture seule. Préserver les racines déjà
nécessaires aux autres connexions. Éviter une édition manuelle du `cacerts`
d'un pod, qui disparaîtrait lors de sa recréation.

Exemple exécuté dans un environnement de construction avec le même JDK/JRE
que l'application. Le chemin ci-dessous convient aux distributions récentes
courantes ; vérifier le chemin réel et le type du magasin de l'image.

```bash
BUILD_DIR="$(mktemp -d)"
TRUSTSTORE_FILE="$BUILD_DIR/cacerts"
BASE_CACERTS="${JAVA_HOME:?JAVA_HOME doit désigner le JDK utilisé}/lib/security/cacerts"
test -f "$BASE_CACERTS"
cp "$BASE_CACERTS" "$TRUSTSTORE_FILE"
chmod 600 "$TRUSTSTORE_FILE"

read -r -s -p 'Mot de passe du magasin copié : ' TRUSTSTORE_PASSWORD
printf '\n'
export TRUSTSTORE_PASSWORD
keytool -importcert -trustcacerts -noprompt -alias org-root-ca \
  -file "$CA_FILE" -keystore "$TRUSTSTORE_FILE" \
  -storepass:env TRUSTSTORE_PASSWORD
keytool -list -alias org-root-ca -keystore "$TRUSTSTORE_FILE" \
  -storepass:env TRUSTSTORE_PASSWORD
```

`TRUSTSTORE_PASSWORD` doit correspondre au magasin copié ; cet exemple ne
change pas son mot de passe. Employer un alias unique et contrôler le résultat.
La forme `-storepass:env` lit le mot de passe depuis une variable, conformément
au [manuel keytool du JDK 21](https://docs.oracle.com/en/java/javase/21/docs/specs/man/keytool.html).
La protection du fichier ne remplace pas la vérification de la provenance
de la CA. Ne pas commiter le magasin ni son mot de passe.

Si un Secret Kubernetes est utilisé pour la distribution, le créer par le
mécanisme habituel de gestion des secrets. Exemple de préparation locale :

```bash
TRUSTSTORE_SECRET=application-java-truststore
printf '%s' "$TRUSTSTORE_PASSWORD" > "$BUILD_DIR/password"
chmod 600 "$BUILD_DIR/password"
kubectl create secret generic "$TRUSTSTORE_SECRET" -n "$NS" \
  --from-file=cacerts="$TRUSTSTORE_FILE" \
  --from-file=password="$BUILD_DIR/password" \
  --dry-run=client -o yaml | kubectl apply -f -
```

Un Secret nécessite des contrôles d'accès et une protection du stockage du
cluster ; son encodage n'est pas un chiffrement. Ne pas afficher ni enregistrer
le manifeste généré dans le dépôt.

Fragment illustratif à intégrer au Deployment existant. Les noms
`application` et `application-java-truststore` doivent correspondre aux
paramètres choisis. Conserver les autres variables, options Java, volumes et
montages déjà présents :

```yaml
spec:
  template:
    spec:
      containers:
        - name: application
          env:
            - name: TRUSTSTORE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: application-java-truststore
                  key: password
            - name: JAVA_TOOL_OPTIONS
              value: >-
                -Djavax.net.ssl.trustStore=/etc/java-truststore/cacerts
                -Djavax.net.ssl.trustStorePassword=$(TRUSTSTORE_PASSWORD)
          volumeMounts:
            - name: java-truststore
              mountPath: /etc/java-truststore
              readOnly: true
      volumes:
        - name: java-truststore
          secret:
            secretName: application-java-truststore
            items:
              - key: cacerts
                path: cacerts
```

Le Secret et le Deployment doivent être dans le même namespace. Vérifier la
compatibilité du type de truststore avec le JDK ; définir
`javax.net.ssl.trustStoreType` si nécessaire. La référence explicite au magasin
remplace la sélection de confiance par défaut : les CA requises doivent s'y
trouver. Une bibliothèque configurant son propre contexte TLS peut ignorer
ces propriétés ; vérifier le client réellement utilisé.

Le mot de passe contenu dans les options Java peut apparaître dans les logs
de démarrage de la JVM ou des outils d'inspection. Limiter l'accès à ces logs,
ne pas les publier et choisir une méthode de configuration adaptée si ce
comportement est incompatible avec les exigences d'exploitation.

## IP fixe avec hostname conservé

Préférer une résolution DNS gérée. Si une entrée locale au pod est nécessaire,
`hostAliases` permet de conserver `https://api.example.com:8443` dans
l'application tout en fixant sa résolution, comme décrit dans la
[documentation Kubernetes](https://kubernetes.io/docs/tasks/network/customize-hosts-file-for-pods/).
Exemple de patch à examiner avant application : il déclenche un rollout.
Lire d'abord les alias existants. Si une entrée utilise déjà la même IP,
inclure tous ses hostnames à conserver dans le patch, car sa liste peut être remplacée.

```bash
PATCH_FILE="$(mktemp)"
cat > "$PATCH_FILE" <<EOF
{
  "spec": {
    "template": {
      "spec": {
        "hostAliases": [
          {"ip": "$ADDRESS", "hostnames": ["$HOST"]}
        ]
      }
    }
  }
}
EOF
kubectl patch deployment "$DEPLOY" -n "$NS" \
  --type strategic --patch-file "$PATCH_FILE"
rm -f "$PATCH_FILE"
kubectl rollout status deployment/"$DEPLOY" -n "$NS" --timeout=180s
```

Ne pas substituer l'IP au hostname dans l'URL HTTPS. Cette entrée est attachée
au pod et nécessite une maintenance si l'IP change. Avec GitOps, reporter la
configuration dans la source de vérité pour qu'elle soit conservée.

## Vérifier après le déploiement

Après modification de l'image, des montages ou du magasin, attendre le rollout
du Deployment. Une mise à jour du seul contenu d'un Secret ne garantit pas
que la JVM recharge son truststore ; prévoir le redémarrage contrôlé approprié.

```bash
kubectl rollout status deployment/"$DEPLOY" -n "$NS" --timeout=180s
POD="$(python3 projects/kubernetes-runbooks/scripts/ready_pod.py \
  --namespace "$NS" --selector "$SELECTOR")"
kubectl exec -n "$NS" "$POD" -c "$CONTAINER" -- getent hosts "$HOST"
kubectl exec -n "$NS" "$POD" -c "$CONTAINER" -- sh -c '
  unset JAVA_TOOL_OPTIONS
  keytool -list -alias org-root-ca \
    -keystore /etc/java-truststore/cacerts \
    -storepass:env TRUSTSTORE_PASSWORD
'
```

La présence de la CA dans le magasin ne prouve pas son utilisation par le
client Java. Effectuer un appel applicatif contrôlé avec un compte de test,
vérifier la négociation TLS puis le résultat HTTP et fonctionnel. Examiner
les logs dans un espace privé, sans publier tokens, identifiants, données
métier ou variables d'environnement. Prévoir le retour à l'image et au
manifeste antérieurs si le contrôle échoue.

