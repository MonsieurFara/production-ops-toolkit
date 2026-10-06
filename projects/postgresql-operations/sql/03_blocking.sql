\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT pid AS blocked_pid, unnest(pg_blocking_pids(pid)) AS blocking_pid, clock_timestamp()-query_start AS query_age FROM pg_stat_activity WHERE cardinality(pg_blocking_pids(pid))>0;
COMMIT;
