#!/usr/bin/env python3
"""
Tag (and set default) audio language on MKV/MP4 without re-encoding.

Adds:
- Progress bars for big file ops:
  * MKV: backup copy
  * MP4: ffmpeg remux (reads -progress and shows %)
- Quit safely with 'q' at any prompt; full rollback of files touched in this run
- Language menu: 1) English 2) Spanish 3) Manual; also updates track TITLE to match
- Backups policy: by default deletes .bak.* after a fully successful run; keep via --keep-backups
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ---------- small utils ----------

def which_or_die(cmd: str, pkg_hint: str) -> str:
    path = shutil.which(cmd)
    if not path:
        print(f"ERROR: '{cmd}' not in PATH. Install via: sudo apt install -y {pkg_hint}", file=sys.stderr)
        sys.exit(1)
    return path

def run(cmd: List[str], **kwargs) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kwargs)
    return p.returncode, p.stdout, p.stderr

def is_media_file(p: Path) -> bool:
    return p.suffix.lower() in {".mkv", ".mp4", ".m4v"}

def human(v): return v if v else "-"

def human_bytes(n: int) -> str:
    for unit in ("B","KB","MB","GB","TB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"

# ---------- progress UI ----------

def print_bar(prefix: str, frac: float, extra: str = ""):
    frac = min(max(frac, 0.0), 1.0)
    width = 30
    done = int(frac * width)
    bar = "█"*done + "·"*(width-done)
    pct = int(frac*100)
    msg = f"\r{prefix} [{bar}] {pct:3d}% {extra}"
    print(msg, end="", flush=True)

def end_bar():
    print()  # newline

# ---------- rollback tracker ----------

@dataclass
class Change:
    original: Path
    backup: Path

@dataclass
class ChangeTracker:
    keep_backups: bool = False
    changes: List[Change] = field(default_factory=list)

    def record_backup(self, original: Path, backup: Path):
        for c in self.changes:
            if c.original == original:
                return
        self.changes.append(Change(original=original, backup=backup))

    def revert_all(self):
        print("\nReverting all changes from this run...")
        for c in self.changes:
            try:
                if c.backup.exists():
                    c.backup.replace(c.original)
                    print(f"  restored: {c.original}")
            except Exception as e:
                print(f"  WARN: failed to restore {c.original}: {e}")
        print("Rollback complete.")

    def cleanup_backups(self):
        if self.keep_backups:
            print("Keeping backups as requested (--keep-backups).")
            return
        # delete backups after full success
        for c in self.changes:
            try:
                if c.backup.exists():
                    c.backup.unlink()
            except Exception as e:
                print(f"  WARN: failed to delete backup {c.backup}: {e}")

# ---------- probing ----------

def ffprobe_streams(file_path: Path) -> List[Dict]:
    ffprobe = which_or_die("ffprobe", "ffmpeg")
    code, out, err = run([
        ffprobe, "-v", "error",
        "-show_entries", "stream=index,codec_type,codec_name,channels,channel_layout:stream_tags=language,title",
        "-of", "json", str(file_path)
    ])
    if code != 0:
        raise RuntimeError(f"ffprobe failed: {err.strip()}")
    data = json.loads(out or "{}")
    return data.get("streams", [])

def list_audio_streams(file_path: Path) -> List[Dict]:
    streams = ffprobe_streams(file_path)
    audio = []
    for s in streams:
        if s.get("codec_type") != "audio":
            continue
        tags = s.get("tags") or {}
        audio.append({
            "ff_index": s.get("index"),
            "codec": s.get("codec_name"),
            "channels": s.get("channels"),
            "layout": s.get("channel_layout"),
            "language": (tags.get("language") or "und"),
            "title": tags.get("title", "")
        })
    return audio

def ffprobe_duration_seconds(file_path: Path) -> Optional[float]:
    ffprobe = which_or_die("ffprobe", "ffmpeg")
    code, out, err = run([ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(file_path)])
    if code != 0: return None
    try:
        return float(out.strip())
    except Exception:
        return None

# ---------- file ops with progress ----------

def copy_with_progress(src: Path, dst: Path, label: str = "Backing up"):
    total = src.stat().st_size
    copied = 0
    chunk = 16 * 1024 * 1024  # 16MB
    start = time.time()
    with src.open("rb") as r, dst.open("wb") as w:
        while True:
            buf = r.read(chunk)
            if not buf:
                break
            w.write(buf)
            copied += len(buf)
            elapsed = max(time.time() - start, 0.001)
            speed = f"{human_bytes(int(copied/elapsed))}/s"
            print_bar(f"{label}: {src.name}", copied/total, f"{human_bytes(copied)}/{human_bytes(total)} {speed}")
    shutil.copystat(src, dst)
    end_bar()

# ---------- mkv ops ----------

def mkv_backup(file_path: Path) -> Path:
    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = file_path.with_suffix(file_path.suffix + f".bak.{ts}")
    copy_with_progress(file_path, backup, label="Backup MKV")
    return backup

def mkv_apply(file_path: Path, audio_streams: List[Dict], ff_index_selected: int, lang_code: str, title_text: str, tracker: ChangeTracker):
    mkvpropedit = which_or_die("mkvpropedit", "mkvtoolnix")
    # map ff_index -> ordinal aN among AUDIO streams (1-based)
    ord_map = {}
    ordinal = 1
    for s in audio_streams:
        ord_map[s["ff_index"]] = ordinal
        ordinal += 1
    if ff_index_selected not in ord_map:
        raise ValueError("Selected index not in audio streams.")
    sel_ord = ord_map[ff_index_selected]

    # backup first, record for rollback
    backup = mkv_backup(file_path)
    tracker.record_backup(file_path, backup)

    edits = []
    # selected: language + default=1 + name/title
    edits += ["--edit", f"track:a{sel_ord}", "--set", f"language={lang_code}", "--set", "flag-default=1", "--set", f"name={title_text}"]
    # others default=0
    for s in audio_streams:
        if s["ff_index"] == ff_index_selected: continue
        ord_i = ord_map[s["ff_index"]]
        edits += ["--edit", f"track:a{ord_i}", "--set", "flag-default=0"]

    # mkvpropedit is fast; no progress here
    code, out, err = run([mkvpropedit, str(file_path)] + edits)
    if code != 0:
        raise RuntimeError(f"mkvpropedit failed: {err.strip()}")

# ---------- mp4 ops (ffmpeg with progress) ----------

def ffmpeg_remux_with_progress(src: Path, dst: Path, args: List[str], duration_s: Optional[float]):
    """
    Run ffmpeg with -progress pipe:1 and show % based on out_time_ms.
    args should contain the mapping/copy/disposition/metadata bits (excluding -i/-progress/-loglevel/-nostats and output).
    """
    ffmpeg = which_or_die("ffmpeg", "ffmpeg")
    cmd = [ffmpeg, "-y", "-nostats", "-loglevel", "error", "-progress", "pipe:1", "-i", str(src)] + args + [str(dst)]
    # Use Popen to read progress from stdout
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    frac = 0.0
    try:
        if proc.stdout is not None:
            for line in proc.stdout:
                line = line.strip()
                if line.startswith("out_time_ms=") and duration_s and duration_s > 0:
                    # out_time_ms is microseconds; convert to seconds
                    us = int(line.split("=",1)[1])
                    frac = min(us / (duration_s * 1_000_000.0), 1.0)
                    print_bar("Remux MP4", frac)
                elif line.startswith("progress=end"):
                    frac = 1.0
                    print_bar("Remux MP4", frac)
        proc.wait()
    finally:
        end_bar()
    if proc.returncode != 0:
        _, err = proc.communicate()
        raise RuntimeError(f"ffmpeg failed with code {proc.returncode}. {err}")

def mp4_apply(file_path: Path, audio_streams: List[Dict], ff_index_selected: int, lang_code: str, title_text: str, tracker: ChangeTracker):
    # backup original first for rollback
    ts = time.strftime("%Y%m%d-%H%M%S")
    backup = file_path.with_suffix(file_path.suffix + f".bak.{ts}")
    copy_with_progress(file_path, backup, label="Backup MP4")
    tracker.record_backup(file_path, backup)

    # find index within audio-only list for ffmpeg's :a:N
    audio_ff_indices = [s["ff_index"] for s in audio_streams]
    if ff_index_selected not in audio_ff_indices:
        raise ValueError("Selected audio index not present.")
    a_pos = audio_ff_indices.index(ff_index_selected)  # 0-based

    dst = file_path.with_suffix(".tmp" + file_path.suffix)
    duration_s = ffprobe_duration_seconds(file_path)

    args = [
        "-map", "0",
        "-c", "copy",
        "-disposition:a", "0",
        "-disposition:a:%d" % a_pos, "default",
        "-metadata:s:a:%d" % a_pos, f"language={lang_code}",
        "-metadata:s:a:%d" % a_pos, f"title={title_text}",
        "-movflags", "use_metadata_tags",
    ]
    ffmpeg_remux_with_progress(file_path, dst, args, duration_s)

    dst.replace(file_path)

# ---------- prompts / flow ----------

class UserCancelled(Exception): pass

def prompt_line(msg: str, allow_empty=False) -> str:
    while True:
        ans = input(msg).strip()
        if ans.lower() in {"q", "quit"}:
            raise UserCancelled
        if ans == "" and not allow_empty:
            continue
        return ans

def prompt_int(msg: str, choices: List[int], default: Optional[int] = None) -> int:
    s_choices = "[" + ", ".join(map(str, choices)) + "]"
    while True:
        ans = input(f"{msg} {s_choices}{(' (default ' + str(default) + ')') if default is not None else ''}: ").strip().lower()
        if ans in {"q", "quit"}: raise UserCancelled
        if ans == "" and default is not None: return default
        if ans.isdigit():
            v = int(ans)
            if v in choices: return v
        print("Invalid selection. Enter one of:", ", ".join(map(str, choices)), "or 'q' to cancel.")

def prompt_lang_menu(default_code: str = "eng") -> Tuple[str, str]:
    print("\nLanguage to set on the chosen audio track:")
    print("  1) English (eng)")
    print("  2) Spanish (spa)")
    print("  3) Manual (enter code and title)")
    while True:
        ans = input("Choose 1/2/3 (or 'q' to cancel): ").strip().lower()
        if ans in {"q", "quit"}: raise UserCancelled
        if ans in {"1", "eng"}:
            return "eng", "English"
        if ans in {"2", "spa", "es", "es-ES"}:
            return "spa", "Spanish"
        if ans == "3":
            code = prompt_line("Enter language code (e.g., eng, spa, en-US): ")
            # default title guess
            default_title = {"eng": "English", "spa": "Spanish"}.get(code.lower(), code)
            title = input(f"Enter track title (default '{default_title}'): ").strip() or default_title
            return code, title
        print("Please enter 1, 2, 3 or 'q' to cancel.")

def suggest_audio_index(audio_streams: List[Dict]) -> int:
    eng_idxs = [s["ff_index"] for s in audio_streams
                if (s["language"] or "").lower().startswith("en") or ("english" in (s["title"] or "").lower())]
    if eng_idxs:
        return eng_idxs[0]
    # fallback: highest channels
    best = max(audio_streams, key=lambda s: (s.get("channels") or 0, -s["ff_index"]))
    return best["ff_index"]

def handle_file(file_path: Path, tracker: ChangeTracker):
    print(f"\n—— {file_path} ——")
    try:
        audio = list_audio_streams(file_path)
    except Exception as e:
        print(f"ERROR: probe failed: {e}")
        return

    if not audio:
        print("No audio streams found; skipping.")
        return

    # display table
    print("Audio tracks (ffprobe index):")
    print(" idx | codec   | ch | layout      | lang | title")
    print("-----+---------+----+-------------+------+----------------")
    for s in audio:
        print(f"{s['ff_index']:>3} | {human(s['codec']):8} | {str(human(s['channels'])):>2} | "
              f"{(human(s['layout'])):11} | {s['language'][:4]:4} | {human(s['title'])}")

    # choose track
    suggested = suggest_audio_index(audio)
    choices = [s["ff_index"] for s in audio]
    chosen = prompt_int("Select audio ffprobe index to set as DEFAULT + tag", choices, default=suggested)

    # choose language via menu (eng/spa/manual + title update)
    lang_code, title_text = prompt_lang_menu(default_code="eng")

    # do it
    try:
        ext = file_path.suffix.lower()
        if ext == ".mkv":
            which_or_die("mkvpropedit", "mkvtoolnix")
            mkv_apply(file_path, audio, chosen, lang_code, title_text, tracker)
        elif ext in {".mp4", ".m4v"}:
            mp4_apply(file_path, audio, chosen, lang_code, title_text, tracker)
        else:
            print(f"Skipping unsupported extension: {ext}")
            return
        print(f"OK: updated → default audio idx {chosen}, language={lang_code}, title='{title_text}'")
    except Exception as e:
        print(f"ERROR updating: {e}")
        # best-effort revert for this file
        for c in tracker.changes:
            if c.original == file_path and c.backup.exists():
                try:
                    c.backup.replace(c.original)
                    print("Reverted this file from backup.")
                except Exception as ex:
                    print(f"WARN: revert failed: {ex}")

def walk_path(target: Path, tracker: ChangeTracker):
    if target.is_file():
        if is_media_file(target):
            handle_file(target, tracker)
        else:
            print(f"Skipping non-media file: {target}")
        return
    for root, _, files in os.walk(target):
        for name in sorted(files):
            p = Path(root) / name
            if is_media_file(p):
                handle_file(p, tracker)

def main():
    parser = argparse.ArgumentParser(description="Set default audio & language on MKV/MP4 (eng/spa/manual) without re-encode.")
    parser.add_argument("path", help="File or directory (movie or TV path)")
    parser.add_argument("--keep-backups", action="store_true", help="Keep .bak.* files after success (default is delete).")
    args = parser.parse_args()

    which_or_die("ffprobe", "ffmpeg")
    which_or_die("ffmpeg", "ffmpeg")

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"ERROR: path not found: {target}", file=sys.stderr)
        sys.exit(1)

    tracker = ChangeTracker(keep_backups=args.keep_backups)
    try:
        walk_path(target, tracker)
        tracker.cleanup_backups()
        print("\nDone.")
    except KeyboardInterrupt:
        tracker.revert_all()
        print("\nCancelled (Ctrl+C).")
        sys.exit(130)
    except Exception as e:
        tracker.revert_all()
        print(f"\nFailed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
