-- Candidats nouveaux, pas une transcription garantie des anciens scripts.
-- Vérifier index existants, taille, plan EXPLAIN et effet avant exécution.
-- CREATE INDEX CONCURRENTLY s'exécute hors bloc transactionnel.
-- Lancer chaque commande séparément et vérifier indisvalid/indisready ensuite.
\set ON_ERROR_STOP on
CREATE INDEX CONCURRENTLY IF NOT EXISTS ops_ru_execution_root_procdef
 ON public.act_ru_execution(proc_def_id_) WHERE parent_id_ IS NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS ops_ru_task_procinst
 ON public.act_ru_task(proc_inst_id_);
