# Registres et containerd

Pour ImagePullBackOff, séparer : résolution DNS, accès TCP/TLS, authentification,
nom de repository et tag. Une réponse `NAME_UNKNOWN` indique un nom absent ;
elle ne se corrige pas en désactivant TLS.

Le fichier d'exemple `examples/registry-https-hosts.toml` utilise HTTPS et une
autorité fournie séparément. Vérifier la version de containerd, le namespace
de configuration CRI et son `config_path`. Conserver une sauvegarde de
`config.toml` et éviter les clés en double avant validation/redémarrage.

Un registre HTTP peut être utilisé dans un laboratoire isolé avec un
`hosts.toml` correspondant au host:port exact. Cette exception doit être
explicite ; elle ne résout pas une image absente. Tester le pull avec le même
runtime et les mêmes droits que le kubelet. Les secrets de registre restent hors Git.
