#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path, PurePosixPath

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def create(root):
    root=Path(root).resolve()
    if not root.is_dir():raise ValueError('Répertoire source requis')
    files={}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():raise ValueError('Symlinks refusés pour un manifeste portable')
        if p.is_file():files[p.relative_to(root).as_posix()]={'size':p.stat().st_size,'sha256':digest(p)}
    return {'algorithm':'sha256','files':files}

def verify(root,manifest):
    root=Path(root).resolve();missing=[];changed=[]
    if manifest.get('algorithm')!='sha256':raise ValueError('Algorithme non pris en charge')
    for name,expected in manifest['files'].items():
        relative=PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('Chemin non sûr dans le manifeste')
        p=(root/name).resolve()
        if not p.is_relative_to(root):raise ValueError('Chemin sortant du répertoire')
        if not p.is_file():missing.append(name)
        elif p.stat().st_size!=expected['size'] or digest(p)!=expected['sha256']:changed.append(name)
    extra=sorted(set(create(root)['files'])-set(manifest['files']))
    return {'missing':missing,'changed':changed,'extra':extra,'matches':not(missing or changed or extra)}

def main():
    p=argparse.ArgumentParser(description='SHA-256 de fichiers locaux ; sans modification des données.')
    p.add_argument('action',choices=['create','verify']);p.add_argument('root',type=Path)
    p.add_argument('--output',type=Path);p.add_argument('--manifest',type=Path);a=p.parse_args()
    if a.action=='create':
        if not a.output:p.error('--output requis')
        if a.output.resolve().is_relative_to(a.root.resolve()):p.error('Le manifeste doit rester hors du répertoire analysé')
        result=create(a.root);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(f'Manifeste écrit : {a.output}');return 0
    if not a.manifest:p.error('--manifest requis')
    result=verify(a.root,json.loads(a.manifest.read_text()));print(json.dumps(result,indent=2));return 0 if result['matches'] else 1

if __name__=='__main__':raise SystemExit(main())
