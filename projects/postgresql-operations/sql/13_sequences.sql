\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT schemaname, sequencename, sequenceowner, start_value, min_value, max_value, increment_by, cycle, last_value FROM pg_sequences WHERE schemaname NOT IN ('pg_catalog','information_schema') ORDER BY schemaname,sequencename;
-- last_value NULL peut venir des droits ou d'une séquence non encore utilisée.
COMMIT;
