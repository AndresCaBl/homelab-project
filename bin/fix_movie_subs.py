#!/usr/bin/env python3
import os, re, sys, shutil
from difflib import SequenceMatcher

# -------- CONFIG --------
ROOT = "/srv/media/movies"
DEFAULT_LANG = "en"   # change to "es" if you want default Spanish instead
VIDEO_EXTS = {'.mkv', '.mp4', '.m4v', '.avi', '.mov'}

# Canonicalize common language tokens -> ISO code
LANG_MAP = {
  'en':'en','eng':'en','english':'en',
  'es':'es','spa':'es','spanish':'es','es-419':'es','es-es':'es',
  'pt':'pt','por':'pt','pt-br':'pt','ptbr':'pt',
  'fr':'fr','fra':'fr','french':'fr',
  'it':'it','ita':'it',
  'de':'de','deu':'de','ger':'de',
  'ru':'ru','rus':'ru',
  'zh':'zh','chi':'zh','chs':'zh','cht':'zh',
  'ja':'ja','jpn':'ja',
  'ko':'ko','kor':'ko'
}
# Tokens that often appear in releases; used to improve matching
RES_TAGS = ['2160p','1080p','720p','480p','x265','hevc','x264','h264','remux','bluray','web','webrip','web-dl','dvdrip','hdr','hdr10','dv','atmos','dts','aac']

def best_video_for(sub_path, videos):
    """Pick best matching video by name similarity and token overlap."""
    sbase = os.path.splitext(os.path.basename(sub_path))[0].lower()
    best, bestscore = None, -1.0
    s_norm = re.sub(r'\W+',' ', sbase)
    for v in videos:
        vbase = os.path.splitext(os.path.basename(v))[0].lower()
        v_norm = re.sub(r'\W+',' ', vbase)
        score = SequenceMatcher(None, s_norm, v_norm).ratio()
        for t in RES_TAGS:
            if t in sbase and t in vbase:
                score += 0.2
        # prefer longer video names a bit (often the main cut)
        score += min(len(vbase)/200.0, 0.4)
        if score > bestscore:
            best, bestscore = v, score
    return best

def parse_lang_flags(name):
    n = name.lower()
    # detect language tokens; keep what exists; normalize to ISO if possible
    m = re.search(r'(en|eng|english|es|spa|spanish|fr|fra|french|pt|por|pt-?br|it|ita|de|deu|ger|ru|rus|zh|chi|chs|cht|ja|jpn|ko|kor)(?!.*[a-z])', n)
    lang = None
    if m:
        lang = LANG_MAP.get(m.group(1).replace('-',''), None)
    if not lang:
        # look anywhere as a fallback
        for k in LANG_MAP:
            if re.search(r'(?:^|[^a-z0-9])'+re.escape(k)+r'(?:[^a-z0-9]|$)', n):
                lang = LANG_MAP[k]; break
    forced = bool(re.search(r'(?:^|[^a-z0-9])(forced|forcedsub)(?:[^a-z0-9]|$)', n))
    hi = bool(re.search(r'(?:^|[^a-z0-9])(sdh|hi|hearing)(?:[^a-z0-9]|$)', n))
    return lang, forced, hi

def ensure_dir(p): os.makedirs(p, exist_ok=True)

APPLY = '--apply' in sys.argv
changed = moved = skipped = 0

# Process each movie folder
for movie_dir in sorted([os.path.join(ROOT, d) for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d))]):
    # videos: only top-level files inside the movie folder (Radarr layout)
    videos = [os.path.join(movie_dir, f) for f in os.listdir(movie_dir)
              if os.path.splitext(f)[1].lower() in VIDEO_EXTS]
    if not videos:
        continue

    # collect .srt in the folder and up to 2 levels below (Subs/, Subtitles/, etc.)
    subs = []
    for root, dirs, files in os.walk(movie_dir):
        depth = root[len(movie_dir):].count(os.sep)
        if depth > 2:
            continue
        for f in files:
            if f.lower().endswith('.srt'):
                subs.append(os.path.join(root, f))

    for s in subs:
        v = best_video_for(s, videos)
        if not v:
            skipped += 1
            print(f"[SKIP] No video match for: {s}")
            continue

        base = os.path.splitext(v)[0]
        lang, forced, hi = parse_lang_flags(os.path.basename(s))

        # If no language tag present, default to DEFAULT_LANG (e.g., 'en')
        if not lang:
            lang = DEFAULT_LANG

        new = f"{base}.{lang}{'.forced' if forced else ''}{'.hi' if hi else ''}.srt"

        # Move from subfolders up next to the video first
        if os.path.dirname(s) != os.path.dirname(v):
            target_dir = os.path.dirname(v)
            ensure_dir(target_dir)
            s_target = os.path.join(target_dir, os.path.basename(s))
            if APPLY:
                if os.path.abspath(s) != os.path.abspath(s_target):
                    try:
                        shutil.move(s, s_target)
                        print(f"[MOVE] {s} -> {s_target}")
                        moved += 1
                        s = s_target
                    except Exception as e:
                        print(f"[SKIP] Move failed {s}: {e}")
                        continue
            else:
                print(f"[DRY] Move up: {s} -> {s_target}")
                s = s_target

        # Rename if needed
        if os.path.abspath(s) != os.path.abspath(new):
            if APPLY:
                final = new
                n = 1
                while os.path.exists(final):
                    name, ext = os.path.splitext(new)
                    final = f"{name}.alt{n}{ext}"
                    n += 1
                try:
                    os.rename(s, final)
                    print(f"[RENAME] {s} -> {final}")
                    changed += 1
                except Exception as e:
                    print(f"[SKIP] Rename failed {s}: {e}")
            else:
                print(f"[DRY] Rename: {s} -> {new}")

print(f"\nSummary: changed={changed}, moved={moved}, skipped={skipped}, mode={'APPLY' if APPLY else 'DRY-RUN'}")
