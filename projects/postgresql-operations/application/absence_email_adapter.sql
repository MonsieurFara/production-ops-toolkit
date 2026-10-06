-- Reconstruction avec table métier générique : adapter le schéma avant utilisation.
-- Colonnes attendues : employee_number, process_instance_id, start_date, end_date, validated.
\set ON_ERROR_STOP on
\set date_start '2026-10-01'
\set date_end '2026-10-31'
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT DISTINCT a.employee_number, a.start_date, a.end_date, u.email
FROM public.business_absence a
JOIN public.act_hi_varinst v ON v.proc_inst_id_=a.process_instance_id
 AND v.name_ IN ('managerEmail','employeeEmail')
JOIN public.users u ON lower(u.email)=lower(v.text_)
WHERE a.start_date >= :'date_start'::date
 AND a.start_date < :'date_end'::date + interval '1 day'
 AND a.validated IS TRUE;
COMMIT;
