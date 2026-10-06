\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
-- Adapter le schéma si la table a été créée ailleurs. Lecture seule.
SELECT id, locked, lockgranted FROM public.databasechangeloglock;
-- Un verrou présent ne prouve pas qu'il est orphelin : vérifier le migrateur actif.
COMMIT;
