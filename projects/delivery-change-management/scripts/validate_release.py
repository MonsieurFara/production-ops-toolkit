#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path

def validate(manifest_path):
    path=Path(manifest_path).resolve();data=json.loads(path.read_text());errors=[]
    for field in ['name','version','change_reference','rollback']:
        if not data.get(field):errors.append('Champ requis : '+field)
    if not isinstance(data.get('artifacts'),list) or not data.get('artifacts'):errors.append('Au moins un artefact requis')
    for artifact in data.get('artifacts',[]):
        name=artifact.get('path','');relative=Path(name)
        candidate=(path.parent/relative).resolve()
        if not name or relative.is_absolute() or not candidate.is_relative_to(path.parent):
            errors.append('Chemin artefact non sûr');continue
        if not candidate.is_file():errors.append('Artefact absent : '+name);continue
        digest=hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest!=artifact.get('sha256'):errors.append('Checksum différent : '+name)
    return {'name':data.get('name'),'version':data.get('version'),'valid':not errors,'errors':errors}

def main():
    p=argparse.ArgumentParser();p.add_argument('manifest');a=p.parse_args()
    result=validate(a.manifest);print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['valid'] else 1

if __name__=='__main__':raise SystemExit(main())
