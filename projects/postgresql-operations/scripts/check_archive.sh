#!/usr/bin/env bash
set -euo pipefail
file=${1:?Fournir une archive PostgreSQL custom, avec gzip optionnel}
if [[ "$file" == *.gz ]]; then
  gzip -t -- "$file"
  gzip -cd -- "$file" | pg_restore --list
else
  pg_restore --list "$file"
fi
