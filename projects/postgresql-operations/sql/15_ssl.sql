\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT a.application_name, a.usename, s.ssl, s.version, s.cipher FROM pg_stat_ssl s JOIN pg_stat_activity a USING(pid) WHERE a.datname=current_database();
COMMIT;
