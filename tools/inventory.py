#!/usr/bin/env python3
"""Écrire ou vérifier l'inventaire SHA-256 des fichiers de la collection."""
import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'docs' / 'FILE-INVENTORY.sha256'
EXCLUDED = {'.git', '__pycache__', 'node_modules', '.venv', 'output', 'artifacts'}


def render():
    files = sorted((
        p for p in ROOT.rglob('*')
        if p.is_file() and p != INVENTORY
        and not EXCLUDED.intersection(p.relative_to(ROOT).parts)
        and p.suffix not in {'.pyc', '.pyo'}
    ), key=lambda p: p.relative_to(ROOT).as_posix())
    return ''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n'
        for p in files
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true', help='Actualiser le fichier d’inventaire')
    mode.add_argument('--check', action='store_true', help='Vérifier l’inventaire (par défaut)')
    args = parser.parse_args()
    expected = render()
    if args.write:
        INVENTORY.write_text(expected, encoding='utf-8', newline='\n')
    elif not INVENTORY.is_file() or INVENTORY.read_text(encoding='utf-8') != expected:
        parser.exit(1, 'Inventaire différent : exécuter python3 tools/inventory.py --write\n')
    print(f'Inventaire SHA-256 : {len(expected.splitlines())} fichiers + inventaire, OK')


if __name__ == '__main__':
    main()
