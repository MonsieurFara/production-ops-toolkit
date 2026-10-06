#!/usr/bin/env python3
import argparse, json, subprocess, sys

def select_ready(items):
    ready=[]
    for pod in items:
        meta=pod.get('metadata',{});status=pod.get('status',{})
        containers=status.get('containerStatuses',[])
        if meta.get('deletionTimestamp') or status.get('phase')!='Running': continue
        if not containers or not all(c.get('ready') for c in containers): continue
        if not any(c.get('type')=='Ready' and c.get('status')=='True' for c in status.get('conditions',[])): continue
        ready.append(meta['name'])
    if len(ready)!=1: raise ValueError(f'Un pod prêt attendu ; {len(ready)} trouvé(s)')
    return ready[0]

def main():
    p=argparse.ArgumentParser(description='Sélectionner exactement un pod Running et Ready.')
    p.add_argument('--namespace',required=True);p.add_argument('--selector',required=True);a=p.parse_args()
    try:
        result=subprocess.run(['kubectl','get','pods','-n',a.namespace,'-l',a.selector,'-o','json'],capture_output=True,text=True,check=True)
        print(select_ready(json.loads(result.stdout)['items']))
    except (ValueError,KeyError,subprocess.CalledProcessError,FileNotFoundError) as e:
        print(str(e) if isinstance(e,ValueError) else 'Lecture kubectl impossible',file=sys.stderr);return 2
    return 0

if __name__=='__main__': raise SystemExit(main())
