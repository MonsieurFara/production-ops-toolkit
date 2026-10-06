\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT authorized, deleted, count(*) AS accounts
FROM public.alf_auth_status GROUP BY authorized,deleted;
-- Ce diagnostic ne révoque aucune licence. Utiliser l'UI/API prévue par ACS.
COMMIT;
