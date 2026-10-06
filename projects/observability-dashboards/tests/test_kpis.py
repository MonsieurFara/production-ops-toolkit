import importlib.util,pathlib,unittest
BASE=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('kpis',BASE/'scripts/calculate_kpis.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class KpiTests(unittest.TestCase):
 def test_apdex_boundaries_and_errors(self):
  data=[{'latency_ms':'500','status_code':'200'},{'latency_ms':'2000','status_code':'200'},
        {'latency_ms':'2001','status_code':'200'},{'latency_ms':'10','status_code':'500'}]
  k=m.traffic_kpis(data);self.assertEqual(k['apdex'],.375);self.assertEqual(k['server_error_pct'],25)
 def test_empty_has_no_false_success(self):
  self.assertIsNone(m.traffic_kpis([])['apdex']);self.assertIsNone(m.workflow_kpis([])['closure_pct'])
 def test_negative_latency_rejected(self):
  with self.assertRaises(ValueError):m.traffic_kpis([{'latency_ms':'-1','status_code':'200'}])
 def test_non_finite_latency_rejected(self):
  with self.assertRaises(ValueError):m.traffic_kpis([{'latency_ms':'nan','status_code':'200'}])
 def test_workflow_duplicates_rejected(self):
  with self.assertRaises(ValueError):m.workflow_kpis([{'id':'same','process':'demo','status':'active'}]*2)
 def test_open_incidents_excluded_from_mttr(self):
  d=m.rows(BASE/'examples/incidents.csv');k=m.incident_kpis(d)
  self.assertEqual(k['mttr_minutes'],40);self.assertEqual(k['open_incidents'],1);self.assertEqual(k['mttd_minutes'],19/3)
 def test_invalid_incident_order_rejected(self):
  with self.assertRaises(ValueError):m.incident_kpis([{'opened_at':'2026-10-06T10:00:00+00:00','detected_at':'2026-10-06T09:00:00+00:00','closed_at':''}])
 def test_vega_uses_dashboard_timepicker(self):
  import json
  for name in ['cpu','memory']:
   d=json.loads((BASE/'dashboards/vega'/f'{name}.json').read_text());url=d['data'][0]['url']
   self.assertTrue(url['%context%']);self.assertEqual(url['%timefield%'],'@timestamp');self.assertNotIn('query',url['body'])
