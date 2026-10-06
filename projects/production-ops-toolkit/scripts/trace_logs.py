#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path

def redact(line):
    line=re.sub(r'(?i)(authorization\s*[:=]\s*bearer\s+)\S+',r'\1<MASQUE>',line)
    line=re.sub(r'(?i)((?:password|passwd|api[-_]?key|secret)\s*[:=]\s*)[^\s,;]+',r'\1<MASQUE>',line)
    line=re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b','<EMAIL>',line)
    return line

def matches(files, identifiers, show=False):
    for filename in files:
        hits=0
        with Path(filename).open(errors='replace') as src:
            for number,line in enumerate(src,1):
                if any(identifier in line for identifier in identifiers):
                    hits+=1
                    if show: yield {'file':str(filename),'line':number,'text':redact(line.rstrip())}
        yield {'file':str(filename),'matches':hits}

def main():
    p=argparse.ArgumentParser(description='Recherche littérale ; comptes seuls par défaut.')
    p.add_argument('--id',action='append',required=True); p.add_argument('--files',nargs='+',required=True)
    p.add_argument('--show-lines',action='store_true'); a=p.parse_args()
    if any(not x for x in a.id): p.error('Identifiant vide interdit')
    for record in matches(a.files,a.id,a.show_lines): print(json.dumps(record,ensure_ascii=False))

if __name__=='__main__': main()
