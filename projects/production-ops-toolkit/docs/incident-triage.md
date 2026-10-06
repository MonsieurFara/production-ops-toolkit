# Investigation d'un incident

1. Noter heure, symptôme, périmètre, dernière modification et effet utilisateur.
2. Vérifier la ressource locale, l'écoute, le DNS et l'accessibilité depuis le consommateur.
3. Séparer TCP, TLS, HTTP, authentification et logique applicative.
4. Corréler les traces à partir d'identifiants fournis ; garder les logs en local.
5. Formuler une hypothèse vérifiable et un test qui peut l'infirmer.
6. Préparer la correction et son retour arrière, puis valider le parcours fonctionnel.

| Observation | Piste à vérifier |
|---|---|
| Connection refused | Écoute, service arrêté, cible ou port incorrect |
| Timeout | Routage, filtrage, saturation, dépendance bloquée |
| Erreur TLS | SNI, SAN, date, autorité racine et chaîne intermédiaire |
| HTTP 401/403 | Identité, jeton, permissions ou en-tête attendu |
| HTTP 404 | Route, préfixe, méthode et déploiement |
| API OK, navigateur bloqué | Préflight et politique CORS de l'origine exacte |
| HTTP 5xx | Erreur interne ; conserver un identifiant de corrélation et lire les traces |

Un préflight réussi ne prouve pas que le GET métier réussit. Un GET réussi
ne prouve pas que les en-têtes sont acceptés par le navigateur. Tester les deux.
