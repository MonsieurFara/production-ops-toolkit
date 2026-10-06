\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT grantee, table_schema, table_name, privilege_type FROM information_schema.role_table_grants WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY grantee,table_schema,table_name,privilege_type;
COMMIT;
