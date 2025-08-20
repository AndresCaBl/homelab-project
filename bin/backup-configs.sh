#!/usr/bin/env bash
set -euo pipefail
TS="$(date +%Y%m%d-%H%M%S)"
DEST="/srv/backup/configs-$TS.tgz"
tar -czf "$DEST" /srv/config
echo "Wrote $DEST"
