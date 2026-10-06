#!/usr/bin/env python3
import argparse, json, re, subprocess
from datetime import datetime, timezone
from pathlib import PurePosixPath

def build_plan(namespace,pod,deployment,model_dir,filename,backup_dir):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+\.xml',filename) or filename in ['.xml','..xml']:
        raise ValueError('Un nom de fichier XML précis est requis')
    src=PurePosixPath(model_dir)/filename;backup=PurePosixPath(backup_dir)
    if not src.is_absolute() or not backup.is_absolute() or '..' in src.parts or '..' in backup.parts:
        raise ValueError('Chemins absolus sans traversée requis')
    if backup.is_relative_to(PurePosixPath(model_dir)): raise ValueError('Le backup doit être hors du cache des modèles')
    return [
      ['kubectl','exec','-n',namespace,pod,'--','test','-f',str(src)],
      ['kubectl','exec','-n',namespace,pod,'--','test','!','-e',str(backup/filename)],
      ['kubectl','exec','-n',namespace,pod,'--','mkdir','-p',str(backup)],
      ['kubectl','exec','-n',namespace,pod,'--','mv',str(src),str(backup/filename)],
      ['kubectl','rollout','restart','deployment/'+deployment,'-n',namespace],
      ['kubectl','rollout','status','deployment/'+deployment,'-n',namespace,'--timeout=300s']]

def main():
    p=argparse.ArgumentParser(description='Plan de quarantaine d’un modèle Solr diagnostiqué ; simulation par défaut.')
    for name in ['namespace','pod','deployment','file','backup-dir']:p.add_argument('--'+name,required=True)
    p.add_argument('--model-dir',default='/opt/alfresco-search-services/data/alfrescoModels')
    p.add_argument('--execute',action='store_true');a=p.parse_args()
    try: plan=build_plan(a.namespace,a.pod,a.deployment,a.model_dir,a.file,a.backup_dir)
    except ValueError as e:p.error(str(e))
    print(json.dumps({'execute':a.execute,'commands':plan},indent=2))
    if a.execute:
        for command in plan:subprocess.run(command,check=True)

if __name__=='__main__':main()
