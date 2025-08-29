#!/usr/bin/env bash
set -euo pipefail
ROOT="/srv/media/movies"
shopt -s nullglob nocaseglob

find "$ROOT" -mindepth 1 -maxdepth 1 -type d -print0 | while IFS= read -r -d '' dir; do
  vids=( "$dir"/*.{mkv,mp4,m4v,avi,mov} )
  [ ${#vids[@]} -eq 0 ] && continue
  main="$(printf '%s\n' "${vids[@]}" | xargs -I{} du -b "{}" 2>/dev/null | sort -nr | head -n1 | cut -f2-)"
  base="${main%.*}"
  for s in "$dir"/*.srt "$dir"/*.SRT; do
    [ -e "$s" ] || continue
    bn="$(basename -- "$s")"
    tag="$(echo "$bn" | sed -E 's/\.srt$//I' | grep -Eo '(en|eng|english|es|spa|spanish|fr|fra|french|pt|por|pt-br|ptbr|it|ita|de|deu|ger|ru|rus|zh|chi|chs|cht|ja|jpn|ko|kor)(\.forced)?(\.hi)?$' || true)"
    if [[ -n "$tag" ]]; then
      new="${base}.${tag}.srt"
    else
      new="${base}.srt"
    fi
    if [[ "$s" != "$new" ]]; then
      echo "Renaming: $s -> $new"
      mv -n -- "$s" "$new"
    fi
  done
done
