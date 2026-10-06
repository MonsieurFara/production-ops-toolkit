\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT pubname, schemaname, tablename FROM pg_publication_tables ORDER BY pubname,schemaname,tablename;
COMMIT;
