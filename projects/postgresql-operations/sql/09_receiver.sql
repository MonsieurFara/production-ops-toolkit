\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT status, receive_start_lsn, written_lsn, flushed_lsn, latest_end_lsn FROM pg_stat_wal_receiver;
SELECT pg_is_in_recovery() AS recovery, pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn(), pg_last_xact_replay_timestamp();
COMMIT;
