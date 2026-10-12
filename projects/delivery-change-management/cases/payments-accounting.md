# Factures et opérations comptables

**Contribution documentée :** Investigation des traces et de la complétude des avis.

**Périmètre générique :** Événement, correlation ID, statut, document et date de finalisation.

**Méthode réutilisable :** Un avis vide et une date absente doivent être documentés séparément du mouvement comptable. Aucune requête de correction comptable réelle n’est fournie.

Ce cas est une capitalisation anonymisée. Les artefacts applicatifs, identités, données métier et dossiers internes sont exclus de la collection publique.

## Paramètre JDBC absent dans un traitement par lots

Un échange récupéré le 12 octobre 2026 rappelle un diagnostic portant sur
une méthode de validation de facture : le deuxième paramètre JDBC, associé
au type, aurait été absent dans un `batchUpdate`. Le message rapporté était
« Pas de valeur spécifiée pour le paramètre 2 ». Le repository Java complet,
la requête complète et une preuve d'exécution du correctif n'ont pas été récupérés.

Exemple reconstruit sur un schéma fictif, avec exactement deux paramètres :

```sql
UPDATE invoice_payment
SET validated = true
WHERE process_id = ? AND payment_type = ?
```

Pour cette requête précise, chaque élément du lot doit renseigner les deux
positions, dans le même ordre :

```java
ps.setString(1, row.processId());
ps.setString(2, row.paymentType());
```

Avec la requête réelle, compter aussi les paramètres du `SET` et de toutes
les conditions. Vérifier chaque branche du code de binding, les types JDBC,
les valeurs nulles et les filtres métier. Tester au moins un lot comportant
plusieurs éléments et plusieurs types ; contrôler le nombre de lignes
modifiées et la transaction. Cet exemple ne définit aucune règle comptable
et ne constitue pas le code source original du service.
