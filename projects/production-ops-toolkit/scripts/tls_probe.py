#!/usr/bin/env python3
import argparse, json, socket, ssl

def main():
    p=argparse.ArgumentParser(description='Vérifier le certificat et le SNI sans désactiver la validation TLS.')
    p.add_argument('host'); p.add_argument('--port',type=int,default=443)
    p.add_argument('--connect-host',help='Adresse de connexion ; host reste le SNI')
    p.add_argument('--cafile'); p.add_argument('--timeout',type=float,default=5)
    a=p.parse_args(); context=ssl.create_default_context(cafile=a.cafile)
    if not 1 <= a.port <= 65535 or a.timeout <= 0: p.error('Port ou timeout invalide')
    try:
        with socket.create_connection((a.connect_host or a.host,a.port),timeout=a.timeout) as raw:
            with context.wrap_socket(raw,server_hostname=a.host) as conn:
                c=conn.getpeercert()
                print(json.dumps({'tls':conn.version(),'subject':c.get('subject'),
                    'issuer':c.get('issuer'),'not_after':c.get('notAfter'),'verified':True}))
    except (OSError,ssl.SSLError):
        print(json.dumps({'verified':False,'error':'connexion-ou-certificat'})); return 1
    return 0

if __name__=='__main__': raise SystemExit(main())
