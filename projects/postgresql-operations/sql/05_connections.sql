\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT datname, state, count(*) AS sessions FROM pg_stat_activity GROUP BY datname,state ORDER BY datname,state;
COMMIT;
