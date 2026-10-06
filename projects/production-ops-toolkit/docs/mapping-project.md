# Cartographie technique

Deux cartes HTML d'infrastructure optique ont été retrouvées dans les sources.
Elles comportent des localisations réelles, conservées hors de la collection
publique. Le module public reprend le besoin de conversion et de contrôle
de points avec un CSV et un GeoJSON **entièrement fictifs**.

```bash
python3 scripts/csv_to_geojson.py examples/synthetic-map-points.csv --output artifacts/demo.geojson
```

L'ordre GeoJSON est longitude puis latitude. Les IDs doivent être uniques et
les coordonnées valides. Un fichier géographique interne ne doit pas être
publié en remplaçant uniquement son titre : il faut retirer les géométries,
adresses, popups, descriptions et références opérationnelles réelles.
