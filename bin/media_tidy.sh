#!/usr/bin/env bash
set -euo pipefail

ROOTS=(
  "/srv/media/movies"
  "/srv/media/tv"
)
VERIFY="/srv/media/verify"
LOG="$VERIFY/media_tidy_$(date +%F_%H%M).log"

# Change to APPLY=1 to actually make changes.
APPLY="${APPLY:-0}"

# Filetype allow-list (kept). Everything else is considered clutter.
VID_RE='.*\.(mkv|mp4|avi|mov)$'
SUB_RE='.*\.(srt|ass|sub|vtt)$'

# Common junk to remove (torrent/mac/win artifacts)
JUNK_RE='.*\.(nfo|sfv|txt|jpg|jpeg|png|gif|bmp)$'
CRUFT_NAMES_RE='(^|.*/)(Thumbs\.db|thumbs\.db|Desktop\.ini|desktop\.ini|\.DS_Store|\.Spotlight-V100|\.Trashes)$'

exec > >(tee -a "$LOG") 2>&1
echo "=== media_tidy started $(date) (APPLY=$APPLY) ==="

for ROOT in "${ROOTS[@]}"; do
  [ -d "$ROOT" ] || { echo "SKIP missing: $ROOT"; continue; }
  echo
  echo "--- Processing $ROOT ---"

  # 1) Ownership
  echo "[1] Ownership -> andres:andres"
  if [ "$APPLY" = "1" ]; then
    sudo chown -R andres:andres "$ROOT"
  else
    echo "DRY-RUN: sudo chown -R andres:andres \"$ROOT\""
  fi

  # 2) Permissions: dirs 755, files 644
  echo "[2] Permissions (dirs 755, files 644)"
  if [ "$APPLY" = "1" ]; then
    find "$ROOT" -type d -exec chmod 755 {} +
    find "$ROOT" -type f -exec chmod 644 {} +
  else
    echo "DRY-RUN: find \"$ROOT\" -type d -exec chmod 755 {} +"
    echo "DRY-RUN: find \"$ROOT\" -type f -exec chmod 644 {} +"
  fi

  # 3) Remove executable bit on media files, if any slipped through
  echo "[3] Strip exec bit on media files (if any)"
  if [ "$APPLY" = "1" ]; then
    find "$ROOT" -type f -perm /111 -regextype posix-extended \
      \( -iregex "$VID_RE" -o -iregex "$SUB_RE" \) -exec chmod 644 {} +
  else
    find "$ROOT" -type f -perm /111 -regextype posix-extended \
      \( -iregex "$VID_RE" -o -iregex "$SUB_RE" \) -print | sed 's/^/DRY-RUN chmod 644 /'
  fi

  # 4) Delete "Subs" directories that contain only subtitle files (no videos/other files)
  echo "[4] Prune Subs/ folders that only contain subtitles"
  while IFS= read -r d; do
    # Any non-sub files inside?
    if [ -z "$(find "$d" -type f -regextype posix-extended ! -iregex "$SUB_RE" -print -quit)" ]; then
      if [ "$APPLY" = "1" ]; then
        rm -rf -- "$d"
        echo "DEL dir: $d"
      else
        echo "DRY-RUN rm -rf -- \"$d\""
      fi
    fi
  done < <(find "$ROOT" -type d -iname "Subs")

  # 5) Remove obvious junk files (nfo/txt/jpg/png/gif/bmp) & OS cruft
  echo "[5] Remove junk and OS cruft"
  # OS cruft by exact names
  while IFS= read -r f; do
    if [ "$APPLY" = "1" ]; then
      rm -f -- "$f"
      echo "DEL cruft: $f"
    else
      echo "DRY-RUN rm -f -- \"$f\""
    fi
  done < <(find "$ROOT" -type f -regextype posix-extended -iregex "$CRUFT_NAMES_RE")

  # Torrent artifacts & poster/jpgs left in media dirs (Jellyfin will fetch artwork separately)
  while IFS= read -r f; do
    # Keep only if NOT a video/subtitle
    if ! [[ "$f" =~ $VID_RE ]] && ! [[ "$f" =~ $SUB_RE ]]; then
      if [ "$APPLY" = "1" ]; then
        rm -f -- "$f"
        echo "DEL junk: $f"
      else
        echo "DRY-RUN rm -f -- \"$f\""
      fi
    fi
  done < <(find "$ROOT" -type f -regextype posix-extended -iregex "$JUNK_RE")

  # 6) Remove any now-empty directories
  echo "[6] Remove empty directories"
  if [ "$APPLY" = "1" ]; then
    find "$ROOT" -type d -empty -delete
  else
    find "$ROOT" -type d -empty -print | sed 's/^/DRY-RUN rmdir /'
  fi

  # 7) Summary per root
  echo "[7] Summary for $ROOT"
  find "$ROOT" -type f -regextype posix-extended -iregex "$VID_RE" | wc -l | xargs echo "Videos:"
  find "$ROOT" -type f -regextype posix-extended -iregex "$SUB_RE" | wc -l | xargs echo "Subtitles:"
  du -sh "$ROOT" 2>/dev/null || true
done

echo "=== media_tidy finished $(date) (APPLY=$APPLY) ==="
