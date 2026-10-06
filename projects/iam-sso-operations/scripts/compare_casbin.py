#!/usr/bin/env python3
import argparse, csv, json
from pathlib import Path

def policies(path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        return {tuple(cell.strip() for cell in row) for row in csv.reader(f) if row and not row[0].startswith('#')}

def compare(reference,candidate):
    expected=policies(reference);actual=policies(candidate)
    return {'missing':sorted(expected-actual),'extra':sorted(actual-expected),'matches':expected==actual}

def main():
    p=argparse.ArgumentParser(description='Comparer deux exports Casbin hors ligne, sans appliquer de politique.')
    p.add_argument('reference');p.add_argument('candidate');a=p.parse_args()
    result=compare(a.reference,a.candidate);print(json.dumps(result,indent=2))
    return 0 if result['matches'] else 1

if __name__=='__main__':raise SystemExit(main())
