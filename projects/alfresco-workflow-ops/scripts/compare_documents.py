#!/usr/bin/env python3
import argparse, base64, json, netrc, re, urllib.request, urllib.error
from pathlib import Path
from urllib.parse import urlencode, urlsplit

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args): return None

def fetch(url,auth_file):
    host=urlsplit(url).hostname
    credentials=netrc.netrc(str(auth_file)).authenticators(host)
    headers={'Accept':'application/json'}
    if credentials:
        login,_,password=credentials
        headers['Authorization']='Basic '+base64.b64encode(f'{login}:{password}'.encode()).decode()
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=10) as response:
        return json.load(response)

def nodes_count(base,folder,get):
    count=0;skip=0
    while True:
        data=get(f'{base}/alfresco/api/-default-/public/alfresco/versions/1/nodes/{folder}/children?'+urlencode({'maxItems':100,'skipCount':skip}))['list']
        entries=data['entries'];count+=sum(bool(x['entry'].get('isFile')) for x in entries)
        if not data.get('pagination',{}).get('hasMoreItems'): return count
        if not entries: raise ValueError('Pagination ACS sans progression')
        skip+=len(entries)

def cmis_count(endpoint,folder,get):
    count=0;skip=0
    query=f"SELECT cmis:objectId FROM cmis:document WHERE IN_FOLDER('{folder}')"
    while True:
        data=get(endpoint+'?'+urlencode({'cmisselector':'query','q':query,'succinct':'true','maxItems':100,'skipCount':skip}))
        rows=data.get('results',[]);count+=len(rows)
        if not data.get('hasMoreItems'): return count
        if not rows: raise ValueError('Pagination CMIS sans progression')
        skip+=len(rows)

def main():
    p=argparse.ArgumentParser(description='Comparer les comptes directs ACS/CMIS avec pagination.')
    p.add_argument('--acs-url',required=True);p.add_argument('--cmis-url',required=True);p.add_argument('--folder',required=True)
    p.add_argument('--netrc-file',type=Path,required=True);p.add_argument('--allow-http',action='store_true');a=p.parse_args()
    if not re.fullmatch(r'[0-9a-fA-F-]{36}',a.folder): p.error('UUID de dossier requis')
    for url in [a.acs_url,a.cmis_url]:
        u=urlsplit(url)
        if u.username or u.password or u.query or not u.hostname: p.error('URL sans identifiants ni query requise')
        if u.scheme!='https' and not (a.allow_http and u.scheme=='http'):p.error('HTTPS requis ; --allow-http pour un laboratoire')
    if a.netrc_file.stat().st_mode & 0o077:p.error('Le fichier netrc doit être privé (chmod 600)')
    get=lambda url:fetch(url,a.netrc_file)
    try:
        acs=nodes_count(a.acs_url.rstrip('/'),a.folder,get);cmis=cmis_count(a.cmis_url,a.folder,get)
    except (OSError,ValueError,KeyError,netrc.NetrcParseError):
        print(json.dumps({'error':'lecture-ACS-ou-CMIS'}));return 2
    print(json.dumps({'nodes_direct_documents':acs,'cmis_direct_documents':cmis,'counts_match':acs==cmis}))
    return 0 if acs==cmis else 1

if __name__=='__main__': raise SystemExit(main())
