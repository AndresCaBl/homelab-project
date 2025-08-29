#!/usr/bin/env bash
set -euo pipefail

OUT="/srv/backup/reports/tv_inventory.csv"
echo "path,size_bytes,size_mb,duration_s,minutes,width,height,codec,mb_per_min,resolution" > "$OUT"

# video extensions we care about
find /srv/media/tv -type f -iregex '.*\.\(mkv\|mp4\|m4v\|avi\|mov\)$' -print0 |
while IFS= read -r -d '' f; do
  size_b=$(stat -c '%s' "$f" 2>/dev/null || echo 0)
  size_mb=$(awk -v b="$size_b" 'BEGIN{printf "%.2f", b/1024/1024}')

  # probe fields (do separate calls for clarity/reliability)
  codec=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=nk=1:nw=1 "$f" 2>/dev/null || echo "")
  width=$(ffprobe -v error -select_streams v:0 -show_entries stream=width       -of default=nk=1:nw=1 "$f" 2>/dev/null || echo 0)
  height=$(ffprobe -v error -select_streams v:0 -show_entries stream=height     -of default=nk=1:nw=1 "$f" 2>/dev/null || echo 0)
  dur_s=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$f" 2>/dev/null | awk '{printf "%.0f",$1}' )
  mins=$(awk -v s="${dur_s:-0}" 'BEGIN{printf "%.2f", (s>0?s/60:0)}')
  mbpm=$(awk -v mb="$size_mb" -v m="$mins" 'BEGIN{printf "%.2f", (m>0?mb/m:0)}')

  # coarse resolution label from height
  res="SD"
  if   ((height>=2160)); then res="2160p"
  elif ((height>=1440)); then res="1440p"
  elif ((height>=1080)); then res="1080p"
  elif ((height>=720));  then res="720p"
  fi

  # CSV line (escape quotes in path)
  p="${f//\"/\"\"}"
  echo "\"$p\",$size_b,$size_mb,${dur_s:-0},$mins,$width,$height,$codec,$mbpm,$res" >> "$OUT"
done

echo "Wrote: $OUT"
