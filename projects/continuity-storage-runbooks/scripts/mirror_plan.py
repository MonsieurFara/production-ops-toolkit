#!/usr/bin/env python3
import argparse,json,re,subprocess

def plan(source,target):
    valid=re.compile(r'[A-Za-z0-9_-]+/[A-Za-z0-9._/-]+')
    if not valid.fullmatch(source) or not valid.fullmatch(target):raise ValueError('Alias/bucket requis, sans option ni identifiants')
    if any(x in ['.','..'] for x in source.split('/')+target.split('/')):raise ValueError('Traversée interdite')
    if source==target:raise ValueError('Source et cible identiques')
    return ['mc','mirror',source,target]

def main():
    p=argparse.ArgumentParser(description='Plan de miroir S3 additif ; sans --remove ni --overwrite.')
    p.add_argument('--source',required=True);p.add_argument('--target',required=True);p.add_argument('--execute',action='store_true');a=p.parse_args()
    try:command=plan(a.source,a.target)
    except ValueError as e:p.error(str(e))
    print(json.dumps({'execute':a.execute,'command':command}))
    if a.execute:subprocess.run(command,check=True)

if __name__=='__main__':main()
