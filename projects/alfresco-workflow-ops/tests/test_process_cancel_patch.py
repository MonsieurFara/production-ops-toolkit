import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
SCRIPT = BASE / 'scripts' / 'plan_process_cancel_patch.py'
spec = importlib.util.spec_from_file_location('process_cancel_patch', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ProcessCancelPatchTests(unittest.TestCase):
    def test_recovered_source_plan_and_rollout_checksum(self):
        source = module.SOURCE_PATH.read_bytes().decode('utf-8')
        plan = module.build_plan(source, 'ops-lab', 'aps-lab', 'activiti-app')
        configmap = plan['configmap.json']
        patch = plan['deployment-patch.json']
        self.assertEqual(configmap['apiVersion'], 'v1')
        self.assertEqual(configmap['kind'], 'ConfigMap')
        self.assertEqual(configmap['metadata'], {'name': 'process-cancel-ui', 'namespace': 'ops-lab'})
        self.assertEqual(configmap['data']['process-cancel.html'], source)
        self.assertNotRegex(configmap['data']['process-cancel.html'], r'\bcancel\s*\(')
        self.assertEqual(patch['metadata'], {'name': 'aps-lab', 'namespace': 'ops-lab'})
        pod_template = patch['spec']['template']
        container, = pod_template['spec']['containers']
        self.assertEqual(container['name'], 'activiti-app')
        self.assertNotIn('image', container)
        self.assertNotIn('$patch', container)
        self.assertEqual(container['volumeMounts'], [{
            'name': 'process-cancel-ui', 'mountPath': module.DEFAULT_MOUNT_PATH,
            'subPath': 'process-cancel.html', 'readOnly': True,
        }])
        self.assertEqual(pod_template['spec']['volumes'], [{
            'name': 'process-cancel-ui', 'configMap': {
                'name': 'process-cancel-ui',
                'items': [{'key': 'process-cancel.html', 'path': 'process-cancel.html'}],
            },
        }])
        checksum = pod_template['metadata']['annotations'][module.CHECKSUM_ANNOTATION]
        self.assertEqual(checksum, hashlib.sha256(source.encode('utf-8')).hexdigest())
        updated = module.build_plan(source + '\n<!-- mise à jour -->', 'ops-lab', 'aps-lab', 'activiti-app')
        self.assertNotEqual(checksum, updated['deployment-patch.json']['spec']['template']['metadata']['annotations'][module.CHECKSUM_ANNOTATION])

    def test_invalid_names_and_mount_paths_rejected(self):
        defaults = {'namespace': 'ops-lab', 'deployment': 'aps-lab', 'container': 'activiti-app',
                    'configmap': 'process-cancel-ui', 'mount_path': module.DEFAULT_MOUNT_PATH}
        invalid = {
            'namespace': ['', 'Ops-Lab', 'ops.lab', 'x' * 64, '-lab', 'lab-'],
            'deployment': ['', 'APS', 'bad_name', 'a..b', 'x' * 64, 'a.' * 127 + 'b'],
            'container': ['', 'App', 'app.web', 'x' * 64],
            'configmap': ['', 'Config', 'bad_name', 'a..b', 'x' * 64],
            'mount_path': ['', 'relative/file.html', '/', '//server/file.html', '/a/../b',
                           '/a/./b', '/a//b', '/a/', '/a\\b', '/a\0b'],
        }
        for field, values in invalid.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    arguments = {**defaults, field: value}
                    with self.assertRaises(ValueError):
                        module.build_plan('<button ng-click="$hide()">Fermer</button>', **arguments)

    def test_source_requires_close_only_handler(self):
        for source in ['<button>Fermer</button>', '<button ng-click="cancel()">Annuler</button>',
                       '<button ng-click="$hide(); cancel()">Fermer</button>']:
            with self.subTest(source=source), self.assertRaisesRegex(ValueError, 'cancel'):
                module.build_plan(source, 'ops-lab', 'aps-lab', 'activiti-app')

    def test_existing_output_refused_and_preserved(self):
        plan = module.build_plan('<button ng-click="$hide()">Fermer</button>', 'ops-lab', 'aps-lab', 'activiti-app')
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'plan'
            module.write_plan(output, plan)
            before = {path.name: path.read_bytes() for path in output.iterdir()}
            with self.assertRaises(FileExistsError):
                module.write_plan(output, plan)
            self.assertEqual(before, {path.name: path.read_bytes() for path in output.iterdir()})

    def test_cli_generates_only_two_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'plan'
            result = subprocess.run([
                sys.executable, str(SCRIPT), '--namespace', 'ops-lab', '--deployment', 'aps-lab',
                '--container', 'activiti-app', '--configmap', 'custom-ui',
                '--mount-path', '/opt/aps/process-cancel.html', '--output', str(output),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p.name for p in output.iterdir()}, {'configmap.json', 'deployment-patch.json'})
            configmap = json.loads((output / 'configmap.json').read_text(encoding='utf-8'))
            patch = json.loads((output / 'deployment-patch.json').read_text(encoding='utf-8'))
            self.assertEqual(configmap['metadata']['name'], 'custom-ui')
            pod_spec = patch['spec']['template']['spec']
            self.assertEqual(pod_spec['volumes'][0]['configMap']['name'], 'custom-ui')
            self.assertEqual(pod_spec['containers'][0]['volumeMounts'][0]['mountPath'], '/opt/aps/process-cancel.html')


if __name__ == '__main__':
    unittest.main()
