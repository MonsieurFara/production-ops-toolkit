import importlib.util, pathlib, tempfile, unittest, threading
from http.server import BaseHTTPRequestHandler, HTTPServer

BASE=pathlib.Path(__file__).resolve().parents[1]/'scripts'
def load(name):
    spec=importlib.util.spec_from_file_location(name,BASE/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        if self.path=='/redirect':
            self.send_response(302);self.send_header('Location','/ok')
        else:
            self.send_response(403 if self.path=='/denied' else 200)
            self.send_header('Access-Control-Allow-Origin','https://portal.example.com')
        self.end_headers()

class ProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=HTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls): cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def test_cors_match(self):
        r=load('http_probe').probe(self.url+'/ok','https://portal.example.com')
        self.assertEqual(r['status'],200);self.assertTrue(r['cors_matches'])
    def test_http_error_preserved(self): self.assertEqual(load('http_probe').probe(self.url+'/denied')['status'],403)
    def test_redirect_not_followed(self): self.assertEqual(load('http_probe').probe(self.url+'/redirect')['status'],302)
    def test_literal_search(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'sample.txt';p.write_text('TX.1 ok\nTXx1 other\n')
            self.assertEqual(list(load('trace_logs').matches([p],['TX.1']))[0]['matches'],1)
    def test_secret_masking(self):
        r=load('trace_logs').redact('password=demo-only secret=test-only mail=demo@example.com')
        self.assertNotIn('demo-only',r);self.assertNotIn('test-only',r);self.assertNotIn('demo@example.com',r)
