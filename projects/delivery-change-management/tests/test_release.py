import importlib.util,pathlib,tempfile,unittest,json,hashlib
BASE=pathlib.Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('release',BASE/'scripts/validate_release.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ReleaseTests(unittest.TestCase):
 def test_fixture_valid(self):self.assertTrue(m.validate(BASE/'examples/release.json')['valid'])
 def test_changed_artifact_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'a.txt').write_text('new');(p/'release.json').write_text(json.dumps({'name':'lab','version':'1','change_reference':'demo','rollback':'plan','artifacts':[{'path':'a.txt','sha256':hashlib.sha256(b'old').hexdigest()}]}))
   self.assertFalse(m.validate(p/'release.json')['valid'])
 def test_missing_fields_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'release.json';p.write_text('{}');self.assertFalse(m.validate(p)['valid'])
 def test_traversal_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'release.json';p.write_text(json.dumps({'name':'lab','version':'1','change_reference':'demo','rollback':'plan','artifacts':[{'path':'../outside.txt'}]}));self.assertFalse(m.validate(p)['valid'])
