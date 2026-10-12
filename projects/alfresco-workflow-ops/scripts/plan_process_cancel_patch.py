#!/usr/bin/env python3
"""Générateur public reconstruit : ConfigMap et patch APS, sans déploiement."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

SOURCE_PATH = Path(__file__).resolve().parents[1] / 'examples' / 'process-cancel-close-only.html'
DEFAULT_CONFIGMAP = 'process-cancel-ui'
DEFAULT_MOUNT_PATH = '/usr/local/tomcat/webapps/activiti-app/workflow/views/modal/process-cancel.html'
VOLUME_NAME = 'process-cancel-ui'
HTML_KEY = 'process-cancel.html'
CHECKSUM_ANNOTATION = 'production-ops-toolkit/process-cancel-sha256'
DNS_LABEL = re.compile(r'[a-z0-9](?:[a-z0-9-]*[a-z0-9])?')


def validate_name(value, field, subdomain=False):
    """Noms DNS Kubernetes ; namespace/conteneur sont des labels de 63 caractères."""
    limit = 253 if subdomain else 63
    labels = value.split('.') if isinstance(value, str) else []
    if (not labels or len(value) > limit or (not subdomain and len(labels) != 1)
            or any(len(label) > 63 or not DNS_LABEL.fullmatch(label) for label in labels)):
        raise ValueError(f'{field} : nom DNS Kubernetes invalide')


def validate_mount_path(value):
    if not isinstance(value, str) or '\0' in value or '\\' in value:
        raise ValueError('mount-path : chemin POSIX absolu et normalisé requis')
    path = PurePosixPath(value)
    if (not path.is_absolute() or value.startswith('//') or path == PurePosixPath('/')
            or '..' in path.parts or str(path) != value):
        raise ValueError('mount-path : chemin POSIX absolu et normalisé requis')


def build_plan(source_html, namespace, deployment, container,
               configmap=DEFAULT_CONFIGMAP, mount_path=DEFAULT_MOUNT_PATH):
    """Construire deux documents, à appliquer séparément après revue en laboratoire."""
    validate_name(namespace, 'namespace')
    validate_name(deployment, 'deployment', subdomain=True)
    validate_name(container, 'container')
    validate_name(configmap, 'configmap', subdomain=True)
    validate_mount_path(mount_path)
    if (not isinstance(source_html, str) or not re.search(r'\$hide\s*\(\s*\)', source_html)
            or re.search(r'\bcancel\s*\(\s*\)', source_html)):
        raise ValueError('Le source HTML doit fermer la fenêtre avec $hide(), sans appel à cancel()')
    checksum = hashlib.sha256(source_html.encode('utf-8')).hexdigest()
    configmap_document = {
        'apiVersion': 'v1',
        'kind': 'ConfigMap',
        'metadata': {'name': configmap, 'namespace': namespace},
        'data': {HTML_KEY: source_html},
    }
    deployment_patch = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {'name': deployment, 'namespace': namespace},
        'spec': {'template': {
            'metadata': {'annotations': {CHECKSUM_ANNOTATION: checksum}},
            'spec': {
                'containers': [{
                    'name': container,
                    'volumeMounts': [{
                        'name': VOLUME_NAME, 'mountPath': mount_path,
                        'subPath': HTML_KEY, 'readOnly': True,
                    }],
                }],
                'volumes': [{
                    'name': VOLUME_NAME,
                    'configMap': {
                        'name': configmap,
                        'items': [{'key': HTML_KEY, 'path': HTML_KEY}],
                    },
                }],
            },
        }},
    }
    return {'configmap.json': configmap_document, 'deployment-patch.json': deployment_patch}


def write_plan(output, plan):
    """Créer un nouveau dossier ; aucun dossier ou fichier existant n'est écrasé."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for filename, document in plan.items():
        with (output / filename).open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(document, handle, ensure_ascii=False, indent=2)
            handle.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--namespace', required=True)
    parser.add_argument('--deployment', required=True)
    parser.add_argument('--container', required=True)
    parser.add_argument('--configmap', default=DEFAULT_CONFIGMAP)
    parser.add_argument('--mount-path', default=DEFAULT_MOUNT_PATH)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        # Décoder les octets sans transformer les fins de ligne du source récupéré.
        source_html = SOURCE_PATH.read_bytes().decode('utf-8')
        plan = build_plan(source_html, args.namespace, args.deployment, args.container,
                          args.configmap, args.mount_path)
        write_plan(args.output, plan)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    print(f'Plan écrit : {args.output} (ConfigMap et patch strategic merge ; aucun déploiement)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
