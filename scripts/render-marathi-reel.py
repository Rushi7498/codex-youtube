#!/usr/bin/env python3
"""Local Marathi Reel builder: Edge TTS + timed captions + FFmpeg.

This script only renders local files. It never uploads or publishes anything.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE_DEFAULT = "mr-IN-ManoharNeural"
TIME_RE = re.compile(
    r"(?P<start>(?:\d{2}:)?\d{2}:\d{2}[.,]\d{3})\s+-->\s+"
    r"(?P<end>(?:\d{2}:)?\d{2}:\d{2}[.,]\d{3})"
)


def run(command: list[str], *, cwd: Path = ROOT) -> str:
    result = subprocess.run(
        command, cwd=cwd, text=True, encoding="utf-8",
        errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}"
        )
    return result.stdout


def find_tool(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    # Known WinGet location used by the Windows setup guide.
    base = Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    if base.exists():
        candidates = list(base.glob("Gyan.FFmpeg.Essentials_*/ffmpeg-*-essentials_build/bin/" + name + ".exe"))
        if candidates:
            return str(candidates[-1])
    raise FileNotFoundError(
        f"{name} सापडले नाही. FFmpeg स्थापित करा आणि PATH मध्ये जोडा, "
        "किंवा docs/marathi-reels.md मधील setup सूचना पाहा."
    )


def parse_time(value: str) -> float:
    value = value.replace(",", ".")
    parts = value.split(":")
    if len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    else:
        hours, minutes, seconds = parts
    sec, millis = seconds.split(".")
    return int(hours) * 3600 + int(minutes) * 60 + int(sec) + int(millis) / 1000


def fmt_time(seconds: float) -> str:
    ms = max(0, round(seconds * 1000))
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def vtt_to_srt(vtt_path: Path, srt_path: Path) -> int:
    """Group Edge TTS word-boundary VTT cues into readable Marathi caption lines."""
    text = vtt_path.read_text(encoding="utf-8-sig")
    blocks = re.split(r"\n\s*\n", text.strip())
    words: list[tuple[float, float, str]] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        time_index = next((i for i, line in enumerate(lines) if TIME_RE.search(line)), None)
        if time_index is None:
            continue
        match = TIME_RE.search(lines[time_index])
        assert match
        caption = " ".join(lines[time_index + 1:]).strip()
        caption = re.sub(r"<[^>]+>", "", caption).strip()
        if caption:
            words.append((parse_time(match.group("start")), parse_time(match.group("end")), caption))

    if not words:
        raise ValueError(
            "Edge TTS subtitle VTT मध्ये timed captions सापडले नाहीत. "
            "नेटवर्क/Edge TTS output तपासा."
        )

    groups: list[list[tuple[float, float, str]]] = []
    current: list[tuple[float, float, str]] = []
    current_chars = 0
    for item in words:
        token = item[2]
        should_break = current and (
            current_chars + len(token) + 1 > 26
            or len(current) >= 5
            or current[-1][2].endswith((".", "!", "?", "।", ","))
        )
        if should_break:
            groups.append(current)
            current = []
            current_chars = 0
        current.append(item)
        current_chars += len(token) + (1 if len(current) > 1 else 0)
    if current:
        groups.append(current)

    output: list[str] = []
    for index, group in enumerate(groups, 1):
        caption = " ".join(item[2] for item in group)
        output.extend([
            str(index),
            f"{fmt_time(group[0][0])} --> {fmt_time(group[-1][1])}",
            caption,
            "",
        ])
    srt_path.write_text("\n".join(output), encoding="utf-8-sig")
    return len(groups)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a local Marathi 9:16 Reel preview.")
    parser.add_argument("--project", required=True, help="Project folder name under projects/ (letters, digits, hyphens)")
    parser.add_argument("--voice", default=VOICE_DEFAULT, help=f"Edge TTS voice (default: {VOICE_DEFAULT})")
    parser.add_argument("--video", help="Optional source video path; loops/crops it to 9:16")
    parser.add_argument("--force", action="store_true", help="Replace generated output files only; source files are never changed")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.project):
        parser.error("--project may contain only letters, digits, hyphens, and underscores")

    project = ROOT / "projects" / args.project
    topic_file = project / "topic.txt"
    narration_file = project / "narration.txt"
    if not topic_file.is_file() or not narration_file.is_file():
        raise FileNotFoundError(
            f"Project inputs missing. Create both:\n  {topic_file}\n  {narration_file}\n"
            "Use docs/marathi-reels.md for the project setup."
        )

    topic = topic_file.read_text(encoding="utf-8-sig").strip()
    narration = narration_file.read_text(encoding="utf-8-sig").strip()
    if not topic or not narration:
        raise ValueError("topic.txt आणि narration.txt रिकामे नसावेत.")

    audio_dir = project / "audio"
    captions_dir = project / "captions"
    output_dir = ROOT / "output" / "preview"
    for folder in (audio_dir, captions_dir, output_dir):
        folder.mkdir(parents=True, exist_ok=True)

    audio_path = audio_dir / "narration.mp3"
    vtt_path = captions_dir / "edge-timing.vtt"
    srt_path = captions_dir / "captions.srt"
    output_path = output_dir / f"{args.project}-preview.mp4"
    manifest_path = project / "manifest.json"

    generated = (audio_path, vtt_path, srt_path, output_path, manifest_path)
    if not args.force:
        existing = [str(path.relative_to(ROOT)) for path in generated if path.exists()]
        if existing:
            raise FileExistsError(
                "Generated file(s) already exist; nothing was overwritten:\n  "
                + "\n  ".join(existing)
                + "\nUse --force to replace generated outputs only."
            )

    ffmpeg = find_tool("ffmpeg")
    ffprobe = find_tool("ffprobe")

    # Edge TTS emits word timing metadata into VTT; use that timing rather than guessing.
    run([
        sys.executable, "-m", "edge_tts",
        "--voice", args.voice,
        "--text", narration,
        "--write-media", str(audio_path),
        "--write-subtitles", str(vtt_path),
    ])

    caption_count = vtt_to_srt(vtt_path, srt_path)
    duration_text = run([
        ffprobe, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)
    ]).strip()
    duration = float(duration_text)

    relative_srt = srt_path.relative_to(ROOT).as_posix()
    subtitle_filter = (
        f"subtitles=filename={relative_srt}:"
        "force_style='FontName=Nirmala UI,FontSize=22,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
        "BorderStyle=1,Outline=2,Alignment=2,MarginV=180'"
    )

    video_path: Path | None = None
    if args.video:
        candidate = Path(args.video)
        video_path = (ROOT / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
        if not video_path.is_file():
            raise FileNotFoundError(f"Source video not found: {video_path}")
        command = [
            ffmpeg, "-hide_banner", "-y" if args.force else "-n",
            "-stream_loop", "-1", "-i", str(video_path),
            "-i", str(audio_path),
            "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{subtitle_filter}",
            "-map", "0:v:0", "-map", "1:a:0",
            "-t", f"{duration:.3f}", "-c:v", "libx264", "-preset", "ultrafast",
            "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(output_path),
        ]
    else:
        command = [
            ffmpeg, "-hide_banner", "-y" if args.force else "-n",
            "-f", "lavfi", "-i", f"color=c=0x14243a:s=1080x1920:r=30:d={duration:.3f}",
            "-i", str(audio_path),
            "-vf", subtitle_filter,
            "-map", "0:v:0", "-map", "1:a:0",
            "-t", f"{duration:.3f}", "-c:v", "libx264", "-preset", "ultrafast",
            "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(output_path),
        ]

    render_log = run(command)
    log_path = project / "render.log"
    log_path.write_text(render_log, encoding="utf-8")

    manifest = {
        "topic": topic,
        "voice": args.voice,
        "duration_seconds": round(duration, 3),
        "caption_count": caption_count,
        "source_video": str(video_path) if video_path else None,
        "narration_file": str(narration_file.relative_to(ROOT)),
        "audio_file": str(audio_path.relative_to(ROOT)),
        "subtitle_file": str(srt_path.relative_to(ROOT)),
        "preview_file": str(output_path.relative_to(ROOT)),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "publishing_approved": False,
        "publishing_enabled": False,
        "notes": "Local preview only. Review factual claims, names, captions and media rights before any publication.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("REEL PREVIEW CREATED")
    print(f"Topic:       {topic}")
    print(f"Duration:    {duration:.2f} seconds")
    print(f"Captions:    {caption_count} timed caption blocks")
    print(f"Preview:     {output_path}")
    print(f"Subtitles:   {srt_path}")
    print("Publishing:  DISABLED (manual approval required)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
