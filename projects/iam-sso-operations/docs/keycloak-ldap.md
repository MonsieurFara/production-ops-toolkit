# Keycloak / LDAP

Documenter version, realm, fournisseur LDAP, mode d'édition, attribut de
login, base de recherche, filtres et mappers. Les valeurs d'une ancienne
instance ne doivent pas être supposées valides sur une nouvelle version.

Contrôler import des utilisateurs, pagination, synchronisation complète ou
incrémentale et traitement des comptes désactivés. Les compteurs added/updated
ne prouvent pas que les attributs et droits sont corrects pour chaque compte.
Conserver des échantillons anonymisés et vérifier le parcours d'authentification.

Un refresh token invalide peut venir d'une expiration, révocation, session,
rotation ou configuration cliente. Ne pas résoudre un problème de token en
élargissant les droits. Pour les avertissements proxy/hostname, vérifier la
terminaison TLS et les en-têtes transmis avec la documentation de la version.

Un verrou Liquibase au démarrage doit être rapproché des migrations actives.
La découverte JGroups et la topologie des instances demandent une vérification
distincte du schéma SQL. Préparer une configuration et un rollback par version.
