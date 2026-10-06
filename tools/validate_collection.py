#!/usr/bin/env python3
"""Valider chaque projet dans son dossier, sans contacter une infrastructure."""
from pathlib import Path
import subprocess, sys

root = Path(__file__).resolve().parents[1]
projects = sorted(p for p in (root / 'projects').iterdir() if p.is_dir())
if len(projects) != 9:
    raise SystemExit('La collection doit contenir neuf projets.')
for project in projects:
    print('\nProjet : ' + project.name, flush=True)
    subprocess.run([sys.executable, 'tools/validate.py'], cwd=project, check=True)
    if (project / 'tests').is_dir():
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=project, check=True)
print('\nValidation des neuf projets terminée.')
