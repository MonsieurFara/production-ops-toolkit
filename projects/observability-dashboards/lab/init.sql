-- Laboratoire uniquement : données fictives, aucun schéma applicatif réel.
CREATE SCHEMA IF NOT EXISTS ops_demo;
CREATE TABLE IF NOT EXISTS ops_demo.workflow_run (
  id text PRIMARY KEY,
  process text NOT NULL,
  status text NOT NULL CHECK (status IN ('active','completed','anomaly')),
  started_at timestamptz NOT NULL
);
INSERT INTO ops_demo.workflow_run(id,process,status,started_at)
SELECT 'DEMO-'||n, CASE WHEN n%2=0 THEN 'Documents' ELSE 'Validation' END,
 CASE WHEN n%17=0 THEN 'anomaly' WHEN n%4=0 THEN 'completed' ELSE 'active' END,
 now() - (n%20) * interval '1 day'
FROM generate_series(1,100) AS n ON CONFLICT(id) DO NOTHING;
