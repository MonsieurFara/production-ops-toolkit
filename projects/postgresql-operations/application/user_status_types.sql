\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema='public' AND table_name='users' AND column_name='status';
SELECT status, count(*) AS accounts FROM public.users GROUP BY status;
-- Ne pas traduire une valeur numérique sans sa définition applicative.
COMMIT;
