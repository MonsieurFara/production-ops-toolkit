\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT slot_name, slot_type, active, restart_lsn, confirmed_flush_lsn, wal_status, CASE WHEN pg_is_in_recovery() THEN NULL ELSE pg_wal_lsn_diff(pg_current_wal_lsn(),restart_lsn) END AS retained_wal_bytes FROM pg_replication_slots;
COMMIT;
