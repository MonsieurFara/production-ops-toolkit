#!/usr/bin/env bash
set -euo pipefail
umask 077
parent=${1:-artifacts}
mkdir -p -- "$parent"
out="$parent/linux-$(date -u +%Y%m%dT%H%M%SZ)-$$"
mkdir -- "$out"
date -u --iso-8601=seconds > "$out/time.txt"
uname -srvmo > "$out/kernel.txt"
uptime > "$out/uptime.txt"
df -hT > "$out/filesystems.txt"
free -m > "$out/memory.txt"
ps -eo pid,comm,%cpu,%mem --sort=-%mem > "$out/processes.txt"
if command -v ss >/dev/null; then ss -ltn > "$out/listening-tcp.txt"; fi
if command -v systemctl >/dev/null; then
  systemctl --failed --no-pager > "$out/failed-services.txt" 2>&1 || true
fi
printf 'Collecte locale : %s\n' "$out"
