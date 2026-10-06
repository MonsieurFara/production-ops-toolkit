\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT datname, pg_size_pretty(pg_database_size(oid)) AS size FROM pg_database WHERE datallowconn ORDER BY pg_database_size(oid) DESC;
COMMIT;
