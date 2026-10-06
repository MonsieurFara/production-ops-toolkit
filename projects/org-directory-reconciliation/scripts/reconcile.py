#!/usr/bin/env python3
import argparse,csv,json
from pathlib import Path
from collections import defaultdict,Counter

def read(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))

def plan(source,target):
    by_email=defaultdict(list);by_mat=defaultdict(list)
    for t in target:
        if t.get('email'):by_email[t['email'].strip().casefold()].append(t)
        if t.get('matricule'):by_mat[t['matricule'].strip()].append(t)
    source_mats=Counter(s.get('matricule','').strip() for s in source if s.get('matricule','').strip())
    actions=[]
    for s in source:
        email=s.get('email','').strip().casefold();mat=s.get('matricule','').strip()
        record={'source_matricule':mat}
        if mat and source_mats[mat]>1:actions.append({**record,'action':'skip','reason':'duplicate-source-matricule'});continue
        candidates=by_email[email] if email else []
        if len(candidates)>1:actions.append({**record,'action':'skip','reason':'ambiguous-email'});continue
        if not candidates and mat:candidates=by_mat[mat]
        if len(candidates)>1:actions.append({**record,'action':'skip','reason':'ambiguous-matricule'});continue
        if not candidates:actions.append({**record,'action':'skip','reason':'not-found-no-creation'});continue
        t=candidates[0]
        if mat and t.get('matricule') and mat!=t['matricule'].strip():
            actions.append({**record,'action':'skip','reason':'identity-conflict'});continue
        if not t.get('id') or not t.get('keycloak_id'):
            actions.append({**record,'action':'skip','reason':'missing-authority-link'});continue
        patch={field:s[field].strip() for field in ['unit_code','job_title'] if s.get(field,'').strip() and s[field].strip()!=t.get(field,'').strip()}
        actions.append({**record,'target_id':t['id'],'action':'update' if patch else 'unchanged','patch':patch})
    return {'mode':'offline-plan','actions':actions,'summary':dict(Counter(a['action'] for a in actions))}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--target',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=plan(read(a.source),read(a.target));a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');a.output.chmod(0o600)
    print(json.dumps(result['summary']))

if __name__=='__main__':main()
