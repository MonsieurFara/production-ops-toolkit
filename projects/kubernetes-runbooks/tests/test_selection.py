import importlib.util, pathlib, unittest
BASE=pathlib.Path(__file__).resolve().parents[1]/'scripts'
def load(name):
    s=importlib.util.spec_from_file_location(name,BASE/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def pod(name,ready=True,deleting=False):
    return {'metadata':{'name':name,**({'deletionTimestamp':'2026-10-06'} if deleting else {})},
      'status':{'phase':'Running','containerStatuses':[{'name':'app','ready':ready}], 'conditions':[{'type':'Ready','status':'True' if ready else 'False'}]}}
class SelectionTests(unittest.TestCase):
    def test_excludes_unready_and_deleting(self):
        self.assertEqual(load('ready_pod').select_ready([pod('a'),pod('b',False),pod('c',deleting=True)]),'a')
    def test_ambiguous_refused(self):
        with self.assertRaises(ValueError): load('ready_pod').select_ready([pod('a'),pod('b')])
    def test_empty_refused(self):
        with self.assertRaises(ValueError): load('ready_pod').select_ready([])
    def test_no_secrets_in_snapshot(self):
        p=pod('a');p['spec']={'containers':[{'name':'app','env':[{'name':'SECRET','value':'demo-only'}],'resources':{}}]}
        import json
        self.assertNotIn('demo-only',json.dumps(load('cluster_snapshot').summarize([p],[])))
    def test_binary_and_decimal_units(self):
        m=load('memory_quantity').memory_bytes
        self.assertEqual(m('1Gi'),1073741824);self.assertEqual(m('1G'),1000000000)
    def test_invalid_units(self):
        with self.assertRaises(ValueError):load('memory_quantity').memory_bytes('12Bad')
