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
 def test_invalid_artifact_collections_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'release.json'
   for artifacts in [None,'bad',{'path':'a.txt'},42,[]]:
    with self.subTest(artifacts=artifacts):
     p.write_text(json.dumps({'name':'lab','version':'1','change_reference':'demo','rollback':'plan','artifacts':artifacts}))
     result=m.validate(p);self.assertFalse(result['valid']);self.assertTrue(result['errors'])
 def test_non_object_manifest_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'release.json'
   for data in [None,[],42,'bad',True]:
    with self.subTest(manifest=data):
     p.write_text(json.dumps(data));result=m.validate(p)
     self.assertFalse(result['valid']);self.assertEqual(result['errors'],['Le manifeste doit être un objet'])
 def test_non_object_artifacts_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'release.json'
   for artifact in [None,'a.txt',42,[]]:
    with self.subTest(artifact=artifact):
     p.write_text(json.dumps({'name':'lab','version':'1','change_reference':'demo','rollback':'plan','artifacts':[artifact]}))
     result=m.validate(p);self.assertFalse(result['valid']);self.assertIn('Chaque artefact doit être un objet',result['errors'])
 def test_invalid_artifact_paths_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/'release.json'
   for name in [None,'',42,True,[],{},'invalid\0path',str((pathlib.Path(d)/'absolute.txt').resolve())]:
    with self.subTest(path=name):
     p.write_text(json.dumps({'name':'lab','version':'1','change_reference':'demo','rollback':'plan','artifacts':[{'path':name}]}))
     result=m.validate(p);self.assertFalse(result['valid']);self.assertIn('Chemin artefact non sûr',result['errors'])
