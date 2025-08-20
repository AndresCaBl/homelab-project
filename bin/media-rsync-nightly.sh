#!/usr/bin/env bash
# Option B: keep torrents seeding on SSD; copy completed media to USB nightly.
set -euo pipefail
SRC="/srv/cache/downloads/complete"
MOVIES="/srv/media/movies"
TV="/srv/media/tv"
rsync -a --info=stats1 --exclude=".torrent" "$SRC/movies/" "$MOVIES/"
rsync -a --info=stats1 --exclude=".torrent" "$SRC/tv/" "$TV/"
