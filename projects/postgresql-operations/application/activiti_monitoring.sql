\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
-- Adapter les tables après inventaire ; aucune jointure vers des identités.
SELECT proc_def_id_, count(*) AS running FROM public.act_ru_execution
WHERE parent_id_ IS NULL GROUP BY proc_def_id_ ORDER BY running DESC;
SELECT proc_def_id_, count(*) AS completed FROM public.act_hi_procinst
WHERE end_time_ IS NOT NULL GROUP BY proc_def_id_ ORDER BY completed DESC;
SELECT proc_def_id_, count(*) AS pending_tasks FROM public.act_ru_task
GROUP BY proc_def_id_ ORDER BY pending_tasks DESC;
COMMIT;
