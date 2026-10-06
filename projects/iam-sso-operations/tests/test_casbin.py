import importlib.util,pathlib,unittest,tempfile
BASE=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('casbin',BASE/'scripts/compare_casbin.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CasbinTests(unittest.TestCase):
 def test_missing_policy_reported(self):
  r=m.compare(BASE/'examples/casbin-reference.csv',BASE/'examples/casbin-candidate.csv')
  self.assertEqual(r['missing'],[('p','editor','documents','write')]);self.assertFalse(r['matches'])
 def test_order_and_duplicates_do_not_change_set(self):
  with tempfile.TemporaryDirectory() as d:
   a=pathlib.Path(d)/'a.csv';b=pathlib.Path(d)/'b.csv'
   a.write_text('p,r,x,read\ng,a,r\n');b.write_text('g,a,r\np,r,x,read\np,r,x,read\n')
   self.assertTrue(m.compare(a,b)['matches'])
