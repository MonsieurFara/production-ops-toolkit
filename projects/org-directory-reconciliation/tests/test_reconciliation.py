import importlib.util,pathlib,unittest,tempfile,subprocess,json
BASE=pathlib.Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('reconcile',BASE/'scripts/reconcile.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ReconciliationTests(unittest.TestCase):
 def test_identity_not_overwritten(self):
  result=m.plan(m.read(BASE/'examples/hr.csv'),m.read(BASE/'examples/directory.csv'))
  patch=result['actions'][0]['patch'];self.assertEqual(set(patch),{'unit_code','job_title'})
  self.assertEqual(result['summary'],{'update':1,'unchanged':1,'skip':1})
 def test_ambiguous_email_refused(self):
  target=m.read(BASE/'examples/directory.csv');target.append(dict(target[0],id='duplicate'))
  self.assertEqual(m.plan(m.read(BASE/'examples/hr.csv'),target)['actions'][0]['reason'],'ambiguous-email')
 def test_identity_conflict_refused(self):
  target=m.read(BASE/'examples/directory.csv');target[0]['matricule']='OTHER'
  self.assertEqual(m.plan(m.read(BASE/'examples/hr.csv'),target)['actions'][0]['reason'],'identity-conflict')
 def test_duplicate_source_id_refused(self):
  source=m.read(BASE/'examples/hr.csv');source.append(dict(source[0]))
  self.assertEqual(m.plan(source,m.read(BASE/'examples/directory.csv'))['actions'][0]['reason'],'duplicate-source-matricule')
 def test_recovered_builder_bom_fallback_and_padding(self):
  with tempfile.TemporaryDirectory() as d:
   src=pathlib.Path(d)/'personnel.csv';out=pathlib.Path(d)/'seed.json'
   src.write_text('\ufeff'+(BASE/'examples/personnel.csv').read_text(),encoding='utf-8')
   subprocess.run(['node',str(BASE/'recovered/build_seed_from_personnel.js'),str(src),str(out)],check=True,capture_output=True)
   data=json.loads(out.read_text());self.assertEqual(data['employes'][0]['adresseEmail'],'alice@example.com')
   self.assertTrue(any(u['code']=='00006' for u in data['unites']))
   self.assertTrue(out.with_name('seed.data.js').exists())
