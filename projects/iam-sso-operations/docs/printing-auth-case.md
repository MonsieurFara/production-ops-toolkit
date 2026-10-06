# Cas d'intégration : authentification et autorisation

Un cas de plateforme d'impression a permis de distinguer trois étapes :
authentification Keycloak, résolution des politiques Casbin et exécution des
requêtes de dashboard. Une réponse login 200 ne prouve ni les autorisations
nécessaires ni le bon fonctionnement du dashboard.

Le comparateur Casbin de cette collection est un outil **hors ligne**. Une
copie de politiques entre environnements doit être revue selon rôles et
responsabilités ; elle ne constitue pas une règle générale de correction.
Le backend propriétaire, ses connexions CBS/Informix et ses données restent hors Git.
