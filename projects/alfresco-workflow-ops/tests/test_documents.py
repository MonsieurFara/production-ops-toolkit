import importlib.util, pathlib, unittest
BASE=pathlib.Path(__file__).resolve().parents[1]/'scripts'
def load(name):
 s=importlib.util.spec_from_file_location(name,BASE/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class DocumentsTests(unittest.TestCase):
 def test_direct_files_only_and_pagination(self):
  replies=iter([{'list':{'entries':[{'entry':{'isFile':True}},{'entry':{'isFile':False}}],'pagination':{'hasMoreItems':True}}},
                {'list':{'entries':[{'entry':{'isFile':True}}],'pagination':{'hasMoreItems':False}}}])
  urls=[]
  def get(url):urls.append(url);return next(replies)
  self.assertEqual(load('compare_documents').nodes_count('https://example.com','demo',get),2)
  self.assertIn('skipCount=2',urls[1])
 def test_cmis_pagination(self):
  replies=iter([{'results':[{},{}],'hasMoreItems':True},{'results':[{}],'hasMoreItems':False}])
  self.assertEqual(load('compare_documents').cmis_count('https://example.com','demo',lambda _:next(replies)),3)
 def test_no_progress_rejected(self):
  with self.assertRaises(ValueError):load('compare_documents').cmis_count('https://example.com','demo',lambda _:{'results':[],'hasMoreItems':True})
 def test_plan_has_no_delete_and_explicit_file(self):
  plan=load('solr_model_quarantine').build_plan('lab','solr-1','solr','/data/models','old.xml','/data/backup')
  self.assertFalse(any('rm' in c or 'delete' in c for c in plan))
 def test_path_traversal_refused(self):
  with self.assertRaises(ValueError):load('solr_model_quarantine').build_plan('lab','solr-1','solr','/data/models','../old.xml','/data/backup')
 def test_backup_inside_cache_refused(self):
  with self.assertRaises(ValueError):load('solr_model_quarantine').build_plan('lab','solr-1','solr','/data/models','old.xml','/data/models/backup')
