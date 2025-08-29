#!/usr/bin/env python3
import os, re, csv
from difflib import SequenceMatcher

ROOT="/srv/media/movies"
VIDEO_EXTS={'.mkv','.mp4','.m4v','.avi','.mov'}
LANG_KEYS=['en','eng','english','es','spa','spanish','fr','fra','french','pt','por','pt-br','ptbr','it','ita','de','deu','ger','ru','rus','zh','chi','chs','cht','ja','jpn','ko','kor']
RES_TAGS = ['2160p','1080p','720p','480p','x265','hevc','x264','h264','remux','bluray','web','webrip','web-dl','dvdrip','hdr','hdr10','dv','atmos','dts','aac']

def strip_lang_flags_only(s):
    n = s
    # drop trailing language & flags variants anywhere
    for k in LANG_KEYS + ['forced','forcedsub','sdh','hi','hearing']:
        n = re.sub(r'(?i)(?:^|[^A-Za-z0-9])'+re.escape(k)+r'(?:[^A-Za-z0-9]|$)', ' ', n)
    # collapse separators
    n = re.sub(r'[^A-Za-z0-9\(\)]+',' ', n).strip()
    return n.lower()

def norm_for_score(s):
    # for similarity score we still downplay release tokens, groups, brackets
    s = s.lower()
    s = re.sub(r'[\[\(][^\]\)]*[\]\)]',' ', s)  # remove bracketed text
    for t in RES_TAGS:
        s = re.sub(r'(?:^|[^a-z0-9])'+re.escape(t)+r'(?:[^a-z0-9]|$)',' ', s)
    s = re.sub(r'[^a-z0-9]+',' ', s).strip()
    return s

def best_video_for(sub, videos):
    sbase = os.path.splitext(os.path.basename(sub))[0]
    s_norm = norm_for_score(sbase)
    best, bestscore = None, -1.0
    for v in videos:
        vbase = os.path.splitext(os.path.basename(v))[0]
        v_norm = norm_for_score(vbase)
        score = SequenceMatcher(None, s_norm, v_norm).ratio()
        for t in RES_TAGS:
            if t in sbase.lower() and t in vbase.lower():
                score += 0.2
        score += min(len(vbase)/200.0, 0.4)
        if score>bestscore:
            best, bestscore = v, score
    return best, bestscore

rows=[]
for movie_dir in sorted([os.path.join(ROOT,d) for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT,d))]):
    videos = [os.path.join(movie_dir,f) for f in os.listdir(movie_dir)
              if os.path.splitext(f)[1].lower() in VIDEO_EXTS]
    # subs up to depth 2
    subs=[]
    for root, dirs, files in os.walk(movie_dir):
        if root[len(movie_dir):].count(os.sep) > 2: 
            continue
        for f in files:
            if f.lower().endswith('.srt'):
                subs.append(os.path.join(root,f))
    if not subs: 
        continue
    for s in subs:
        sdir = os.path.dirname(s)
        sfile = os.path.basename(s)
        sbase = os.path.splitext(sfile)[0]
        if not videos:
            rows.append([s,'',sfile,'','','','',0.0,'','no_video_in_folder'])
            continue
        best, score = best_video_for(s, videos)
        vfile = os.path.basename(best) if best else ''
        vbase = os.path.splitext(vfile)[0]
        same_dir = (os.path.dirname(best)==sdir) if best else False
        # NEW: only strip language/flags; do NOT strip [720p]/codecs for equality check
        same_base = (strip_lang_flags_only(sbase) == strip_lang_flags_only(vbase))
        if same_dir and same_base:
            reason = 'ok'
        elif not same_dir and not same_base:
            reason = 'needs_move_and_rename'
        elif not same_dir:
            reason = 'needs_move'
        else:
            reason = 'needs_rename'
        if score < 0.60 and reason != 'ok':
            reason += '_lowconf'
        new = os.path.splitext(best)[0] + '.srt' if best else ''
        rows.append([s, best or '', sfile, vbase, '', '', '', round(score,3), new, reason])

out="/srv/backup/reports/movies_subs_audit.csv"
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out,'w',newline='') as f:
    w=csv.writer(f)
    w.writerow(["sub_path","video_path","sub_name","video_name","lang","forced","hi","match_score","suggested_new_path","reason"])
    w.writerows(rows)
print(out)
