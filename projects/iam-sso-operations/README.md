> Projet de la [collection technique](../../README.md). Exécuter les commandes de ce guide depuis ce dossier. La validation continue est pilotée par le workflow à la racine de la collection.

# IAM / SSO Operations

Audits d'identités, procédures Keycloak/LDAP et contrôles d'accès. Les listes
de comptes et politiques de démonstration sont fictives. Les exemples ne
contiennent aucun droit d'accès issu d'un environnement d'entreprise.

| Dossier | Contenu |
|---|---|
| `powershell/` | Audit AD par email ; plan et modification explicite de l'état d'un compte |
| `scripts/` | Comparaison locale de politiques Casbin, sans écriture |
| `examples/` | CSV fictifs pour audit et changement |
| `docs/` | Fédération LDAP, synchronisation, incidents SSO, doublons Liferay et signatures |
| `kql/` | Exercices Sentinel/Defender pour la préparation SC-200 |

```powershell
.\powershell\Audit-ADAccounts.ps1 -InputFile .\examples\accounts.csv -OutputFile .\output\ad-audit.csv
.\powershell\Set-ADAccountState.ps1 -InputFile .\examples\changes.csv
# Pour vérifier le chemin de mutation sans l'appliquer :
.\powershell\Set-ADAccountState.ps1 -InputFile .\examples\changes.csv -Execute -WhatIf
```

Le module ActiveDirectory et des droits adaptés sont requis. La modification
ne s'exécute que si `-Execute` est fourni et si `ShouldProcess` l'autorise.
Les scripts AD et KQL n'ont pas été exécutés sur AD/Sentinel dans cette session.
Le comparateur Casbin est testé sur des CSV synthétiques.
