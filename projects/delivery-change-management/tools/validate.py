#!/usr/bin/env python3
"""Contrôles locaux sans connexion à une infrastructure."""
from pathlib import Path
import ast, json, re, subprocess, sys

root = Path(__file__).resolve().parents[1]
errors = []
for p in root.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in ['.git', '__pycache__', 'node_modules', '.venv', 'output', 'artifacts']):
        continue
    if p.suffix not in ['.py','.sh','.js','.json','.md','.sql','.yml','.yaml','.ps1','.csv','.kql','.toml','.ini','.svg','.html']:
        continue
    text = p.read_text(encoding='utf-8')
    try:
        if p.suffix == '.json': json.loads(text)
        if p.suffix == '.py': ast.parse(text, filename=str(p))
        if p.suffix == '.sh': subprocess.run(['bash','-n',str(p)], check=True, capture_output=True)
        if p.suffix == '.js': subprocess.run(['node','--check',str(p)], check=True, capture_output=True)
    except (ValueError, SyntaxError, subprocess.CalledProcessError) as e:
        errors.append(f'{p.relative_to(root)}: syntaxe invalide ({type(e).__name__})')
    patterns = [r'\bgh[pousr]_[A-Za-z0-9]{20,}', r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', r'\bAKIA[A-Z0-9]{16}\b']
    if any(re.search(x,text) for x in patterns):
        errors.append(f'{p.relative_to(root)}: motif de secret potentiel')
if errors:
    print('\n'.join(errors), file=sys.stderr); sys.exit(1)
print('Syntaxes Bash / Python / JavaScript / JSON et motifs de secrets : OK')
