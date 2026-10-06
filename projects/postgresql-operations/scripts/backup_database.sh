#!/usr/bin/env bash
set -euo pipefail
umask 077
: "${PGSERVICE:?Définir un service libpq protégé avec PGSERVICE}"
[[ "$PGSERVICE" =~ ^[A-Za-z0-9_-]+$ ]] || { printf 'Nom de service invalide\n' >&2; exit 2; }
parent=${1:-artifacts}
mode=${2:-}
[[ -z "$mode" || "$mode" == --schema-only ]] || { printf 'Option attendue : --schema-only\n' >&2; exit 2; }
mkdir -p -- "$parent"
out="$parent/${PGSERVICE}-$(date -u +%Y%m%dT%H%M%SZ)-$$.dump"
args=(--format=custom --file="$out")
if [[ "$mode" == --schema-only ]]; then args+=(--schema-only); fi
pg_dump --dbname="service=$PGSERVICE" "${args[@]}"
pg_restore --list "$out" > "$out.toc"
sha256sum "$out" > "$out.sha256"
printf 'Archive créée et table des matières lisible : %s\n' "$out"
