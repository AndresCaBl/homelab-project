#!/usr/bin/env bash
set -euo pipefail
echo "[*] Checking /srv mounts and options..."
mount | grep "/srv/media" || { echo "!! /srv/media not mounted"; exit 1; }
grep -E "noatime" /etc/fstab && echo "[*] fstab uses noatime"
df -h /srv/media /srv/cache || true
