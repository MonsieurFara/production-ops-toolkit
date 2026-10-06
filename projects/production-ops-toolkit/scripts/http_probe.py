#!/usr/bin/env python3
"""Code HTTP et CORS ; ne suit pas les redirections et n'affiche pas de secret."""
import argparse, json, time, urllib.request, urllib.error
from pathlib import Path
from urllib.parse import urlsplit

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def probe(url, origin=None, key=None, timeout=5, method='GET'):
    headers = {'Accept': 'application/json'}
    if origin: headers['Origin'] = origin
    if key: headers['X-Intra-Api-Key'] = key
    if method == 'OPTIONS':
        headers['Access-Control-Request-Method'] = 'GET'
        headers['Access-Control-Request-Headers'] = 'X-Intra-Api-Key'
    req = urllib.request.Request(url, headers=headers, method=method)
    start = time.monotonic()
    try:
        response = urllib.request.build_opener(NoRedirect()).open(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        response = e
    with response:
        code = response.code
        h = response.headers
        allowed = h.get('Access-Control-Allow-Origin')
        return {'status': code, 'elapsed_ms': round((time.monotonic()-start)*1000, 2),
                'cors_origin': allowed, 'cors_matches': None if not origin else allowed in (origin, '*'),
                'cors_methods': h.get('Access-Control-Allow-Methods'),
                'cors_headers': h.get('Access-Control-Allow-Headers')}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('url'); p.add_argument('--origin'); p.add_argument('--key-file', type=Path)
    p.add_argument('--timeout', type=float, default=5); p.add_argument('--allow-http', action='store_true')
    p.add_argument('--method', choices=['GET','OPTIONS'], default='GET')
    args=p.parse_args(); parsed=urlsplit(args.url)
    if parsed.username or parsed.password: p.error('Identifiants interdits dans l’URL')
    if parsed.scheme not in ['https','http'] or not parsed.hostname: p.error('URL HTTP(S) requise')
    if parsed.scheme == 'http' and not args.allow_http: p.error('HTTP nécessite --allow-http pour un laboratoire')
    if args.timeout <= 0: p.error('Timeout strictement positif requis')
    key=args.key_file.read_text().strip() if args.key_file else None
    if key and ('\n' in key or '\r' in key): p.error('Clé sur une seule ligne requise')
    try: result=probe(args.url,args.origin,key,args.timeout,args.method)
    except (urllib.error.URLError, TimeoutError, OSError):
        print(json.dumps({'error':'connexion-ou-TLS','status':None})); return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0 if 200 <= result['status'] < 300 else 1

if __name__ == '__main__': raise SystemExit(main())
