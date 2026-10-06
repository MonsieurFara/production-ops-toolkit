#!/usr/bin/env python3
import argparse, json, subprocess
from pathlib import Path
from datetime import datetime, timezone

def get(kind,namespace=None):
    command=['kubectl','get',kind,'-o','json']
    if namespace: command+=['-n',namespace]
    return json.loads(subprocess.run(command,check=True,text=True,capture_output=True).stdout)['items']

def summarize(pods,nodes):
    return {
      'pods':[{'name':p['metadata']['name'],'phase':p.get('status',{}).get('phase'),
        'node':p.get('spec',{}).get('nodeName'),'reason':p.get('status',{}).get('reason'),
        'containers':[{'name':c['name'],'resources':c.get('resources',{})} for c in p.get('spec',{}).get('containers',[])],
        'states':[{'name':c['name'],'ready':c.get('ready'),'restarts':c.get('restartCount'),
        'last_termination_reason':c.get('lastState',{}).get('terminated',{}).get('reason')}
        for c in p.get('status',{}).get('containerStatuses',[])]} for p in pods],
      'nodes':[{'name':n['metadata']['name'],'capacity':n.get('status',{}).get('capacity'),
        'allocatable':n.get('status',{}).get('allocatable'),'conditions':[
        {'type':c['type'],'status':c['status']} for c in n.get('status',{}).get('conditions',[])]} for n in nodes]}

def main():
    p=argparse.ArgumentParser();p.add_argument('--namespace',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=summarize(get('pods',a.namespace),get('nodes'))
    result['captured_at']=datetime.now(timezone.utc).isoformat()
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');a.output.chmod(0o600)
    print(f'Snapshot écrit : {a.output}')

if __name__=='__main__': main()
