import importlib.util,pathlib,tempfile,unittest
BASE=pathlib.Path(__file__).resolve().parents[1]/'scripts'
def load(name):
 s=importlib.util.spec_from_file_location(name,BASE/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class IntegrityTests(unittest.TestCase):
 def test_change_missing_and_extra(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'a').write_text('a');(root/'b').write_text('b');m=load('integrity_manifest');manifest=m.create(root)
   self.assertTrue(m.verify(root,manifest)['matches'])
   (root/'a').write_text('changed');(root/'b').unlink();(root/'extra').write_text('new')
   r=m.verify(root,manifest);self.assertEqual(r['changed'],['a']);self.assertEqual(r['missing'],['b']);self.assertEqual(r['extra'],['extra'])
 def test_traversal_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):load('integrity_manifest').verify(d,{'algorithm':'sha256','files':{'../escape':{'size':0,'sha256':''}}})
 def test_symlink_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'a').write_text('x');(root/'link').symlink_to(root/'a')
   with self.assertRaises(ValueError):load('integrity_manifest').create(root)
 def test_mirror_never_removes_or_overwrites(self):
  self.assertEqual(load('mirror_plan').plan('source/demo','target/demo'),['mc','mirror','source/demo','target/demo'])
 def test_option_injection_rejected(self):
  with self.assertRaises(ValueError):load('mirror_plan').plan('--remove','target/demo')
