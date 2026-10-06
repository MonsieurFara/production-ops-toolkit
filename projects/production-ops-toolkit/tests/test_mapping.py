import importlib.util,pathlib,unittest
p=pathlib.Path(__file__).resolve().parents[1]/'scripts/csv_to_geojson.py'
s=importlib.util.spec_from_file_location('mapping',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class MappingTests(unittest.TestCase):
 def test_coordinate_order(self):
  d=m.convert([{'id':'DEMO','latitude':'20','longitude':'-30'}]);self.assertEqual(d['features'][0]['geometry']['coordinates'],[-30,20])
 def test_invalid_coordinate_rejected(self):
  with self.assertRaises(ValueError):m.convert([{'id':'DEMO','latitude':'91','longitude':'20'}])
 def test_duplicate_rejected(self):
  with self.assertRaises(ValueError):m.convert([{'id':'DEMO','latitude':'20','longitude':'30'}]*2)
