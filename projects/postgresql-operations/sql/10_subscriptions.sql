\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
-- Ne jamais sélectionner subconninfo : elle peut contenir des identifiants.
SELECT subname, subenabled, subpublications FROM pg_subscription;
SELECT subname, pid, relid, received_lsn, last_msg_send_time, last_msg_receipt_time, latest_end_lsn FROM pg_stat_subscription;
COMMIT;
