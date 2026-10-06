\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT n.nspname, c.relname AS index_name, i.indisvalid, i.indisready FROM pg_index i JOIN pg_class c ON c.oid=i.indexrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE NOT i.indisvalid OR NOT i.indisready;
COMMIT;
