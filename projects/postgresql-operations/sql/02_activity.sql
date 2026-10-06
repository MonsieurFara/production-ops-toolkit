\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT pid, usename, application_name, state, wait_event_type, wait_event, clock_timestamp()-query_start AS query_age FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid() ORDER BY query_start NULLS LAST;
COMMIT;
