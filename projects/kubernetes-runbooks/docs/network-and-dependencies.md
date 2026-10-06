# Réseau et dépendances

Tester depuis le pod consommateur avec des outils de diagnostic disponibles :
DNS du Service, EndpointSlices, port cible et protocole applicatif. Une
connexion TCP réussie ne prouve pas le fonctionnement du protocole gRPC.
Vérifier nom pleinement qualifié, namespace, `targetPort`, NetworkPolicies,
TLS et noms du certificat. Pour gRPC, utiliser une requête de santé connue
ou un client documenté plutôt qu'une simple requête HTTP arbitraire.

Pour Nacos, contrôler membres du cluster, namespace/configuration et
dépendances. Pour Temporal, distinguer timeout réseau, namespace inexistant,
TLS, disponibilité du service et erreur de worker. Pour OpenFGA/Liquibase,
observer le Job de migration et ses sorties avant de lancer une seconde copie.

Ingress, Service NodePort et gateway peuvent réécrire les préfixes. Tester
la route depuis chaque point ; comparer l'origine exacte pour CORS.
