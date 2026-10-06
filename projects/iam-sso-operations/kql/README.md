# Exercices KQL — préparation SC-200

Requêtes de laboratoire écrites pour pratiquer la lecture de logs d'identité,
les jointures temporelles et le suivi d'incidents. Ce sont des exercices
originaux, sans questions issues de l'examen officiel.

`SigninLogs` et `SecurityIncident` exigent les connecteurs et tables concernés
dans un workspace. `DeviceLogonEvents` et `DeviceProcessEvents` s'utilisent
dans l'environnement Defender approprié. Vérifier les colonnes avant exécution.
Un indicateur de suspicion n'est pas un verdict ; examiner le contexte et les
preuves. Les résultats contiennent des identités et restent privés.

Sources techniques :
- https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/signinlogs
- https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicelogonevents-table
