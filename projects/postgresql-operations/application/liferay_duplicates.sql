\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
-- Identifier le nom exact de la table et l'adapter si elle a été créée entre guillemets.
SELECT companyid, lower(emailaddress) AS normalized_email, count(*) AS accounts
FROM public.user_ WHERE emailaddress IS NOT NULL AND emailaddress <> ''
GROUP BY companyid,lower(emailaddress) HAVING count(*) > 1;
COMMIT;
