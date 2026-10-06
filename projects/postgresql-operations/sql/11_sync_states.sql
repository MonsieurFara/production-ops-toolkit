\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT s.subname, n.nspname, c.relname, r.srsubstate, r.srsublsn FROM pg_subscription_rel r JOIN pg_subscription s ON s.oid=r.srsubid JOIN pg_class c ON c.oid=r.srrelid JOIN pg_namespace n ON n.oid=c.relnamespace ORDER BY s.subname,n.nspname,c.relname;
-- États documentés : i initial, d copie, f copie terminée, s synchronisé, r prêt.
COMMIT;
