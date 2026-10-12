#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

def validate(manifest_path):
    path=Path(manifest_path).resolve();data=json.loads(path.read_text());errors=[]
    if not isinstance(data,dict):
        return {'name':None,'version':None,'valid':False,'errors':['Le manifeste doit être un objet']}
    for field in ['name','version','change_reference','rollback']:
        if not data.get(field):errors.append('Champ requis : '+field)
    artifacts=data.get('artifacts')
    if not isinstance(artifacts,list) or not artifacts:
        errors.append('Au moins un artefact requis sous forme de liste')
        artifacts=[]
    for artifact in artifacts:
        if not isinstance(artifact,dict):
            errors.append('Chaque artefact doit être un objet');continue
        name=artifact.get('path')
        if not isinstance(name,str) or not name or '\0' in name:
            errors.append('Chemin artefact non sûr');continue
        relative=Path(name)
        try:
            candidate=(path.parent/relative).resolve()
        except (OSError,ValueError):
            errors.append('Chemin artefact non sûr');continue
        if relative.is_absolute() or not candidate.is_relative_to(path.parent):
            errors.append('Chemin artefact non sûr');continue
        if not candidate.is_file():errors.append('Artefact absent : '+name);continue
        digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest!=artifact.get('sha256'):errors.append('Checksum différent : '+name)
    return {'name':data.get('name'),'version':data.get('version'),'valid':not errors,'errors':errors}

def main():
    p=argparse.ArgumentParser();p.add_argument('manifest');a=p.parse_args()
    result=validate(a.manifest);print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['valid'] else 1

if __name__=='__main__':raise SystemExit(main())
