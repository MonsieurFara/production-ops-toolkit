# Scripts retrouvés et adaptations

Les scripts JavaScript proviennent de fichiers retrouvés dans les sources,
avec un guide et une archive concordante. La collection conserve leurs noms
pour faciliter le rapprochement avec les échanges antérieurs. Leurs versions
publiques ont été modifiées ; elles ne sont pas une reproduction bit à bit.

Adaptations : commentaires internes retirés, exemples anonymisés, password
uniquement par environnement, HTTPS exigé sauf localhost, timeout des fetch
et suppression d'une affirmation trompeuse sur l'absence de toute suppression.

## Contrat spécifique

Ces scripts utilisent une API métier contenant des unités, filiales,
référentiels et employés. Leur contrat doit être confronté à la version du
service cible. Les règles de classement des fonctions sont des exemples à
valider, sans attribution implicite de pouvoir de signature.

## Mutation et rollback

Les scripts restent en simulation par défaut. `--execute` effectue des
écritures. Certaines options, dont `--reset-unites` ou `--supprimer-nouveaux`,
sont destructives : elles ne sont pas nécessaires au laboratoire hors ligne.
Conserver le snapshot, sauvegarder la base et vérifier les références avant
toute utilisation. Une restauration fonctionnelle peut recréer des unités
avec de nouveaux IDs ; seule une restauration de base préparée permet de
retrouver intégralement l'état sauvegardé.

Pour la variante Python nouvelle, l'annuaire cible fait autorité sur l'identité.
Les changements de nom, email, rôles ou lien Keycloak restent hors du patch.
Le plan doit être confronté aux unités existantes avant intégration à une API.
