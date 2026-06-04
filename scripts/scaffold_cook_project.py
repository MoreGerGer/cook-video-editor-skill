#!/usr/bin/env python3
"""Create reusable project files for short-form cooking video edits."""

from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import dedent


BUILD_VIDEO = r'''#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="{dish}"
PROJECT_DIR="$OUT_DIR/project"
PLAN="$PROJECT_DIR/clip_plan.tsv"
SEG_DIR="$PROJECT_DIR/segments"
LIST="$PROJECT_DIR/concat_list.txt"
BASE="$PROJECT_DIR/base_no_subtitles.mp4"

if [ ! -f "$PLAN" ]; then
  echo "Missing plan: $PLAN" >&2
  exit 1
fi

rm -rf "$SEG_DIR"
mkdir -p "$SEG_DIR"
: > "$LIST"

tail -n +2 "$PLAN" | while IFS=$'\t' read -r idx src start duration zh en jp pos; do
  [ -n "$idx" ] || continue
  seg="$SEG_DIR/${idx}.mp4"
  ffmpeg -nostdin -hide_banner -loglevel error -y \
    -ss "$start" -i "$src" -t "$duration" \
    -map "0:v:0" -map "0:a:0?" \
    -vf "scale=-2:1920,crop=1080:1920,setsar=1,fps=60" \
    -af "aresample=48000,asetpts=PTS-STARTPTS" \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 128k -shortest "$seg"
  printf "file '%s'\n" "$(pwd)/$seg" >> "$LIST"
done

ffmpeg -nostdin -hide_banner -loglevel error -y -f concat -safe 0 -i "$LIST" -c copy "$BASE"
python3 "$PROJECT_DIR/render_subtitles.py"
'''


RENDER_SUBTITLES = r'''from __future__ import annotations

import csv
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DISH = "{dish}"
OUT_DIR = Path(DISH)
PROJECT_DIR = OUT_DIR / "project"
PLAN = PROJECT_DIR / "clip_plan.tsv"
BASE_VIDEO = PROJECT_DIR / "base_no_subtitles.mp4"
FINAL_VIDEO = OUT_DIR / f"{DISH}.mp4"
SRT = OUT_DIR / f"{DISH}.srt"
JP_SRT = OUT_DIR / f"{DISH}jp.srt"
OVERLAY_DIR = PROJECT_DIR / "subtitle_overlays"
FILTER_FILE = PROJECT_DIR / "subtitle_overlay_filter.txt"
WIDTH = 1080
HEIGHT = 1920
FONT_PATHS = [
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/Library/Fonts/Arial Unicode.ttf"),
]


def font_path() -> str:
    for path in FONT_PATHS:
        if path.exists():
            return str(path)
    raise FileNotFoundError("No CJK-capable font found; install a font that supports Chinese and Japanese")


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def wrap_text(text: str, font: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw, max_width: int) -> list[str]:
    if not text:
        return []
    words = text.split(" ")
    if len(words) > 1:
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if draw.textbbox((0, 0), candidate, font=font, stroke_width=4)[2] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    lines = []
    current = ""
    for ch in text:
        candidate = current + ch
        if draw.textbbox((0, 0), candidate, font=font, stroke_width=4)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def fit_font(texts: list[str], size: int, max_width: int) -> ImageFont.FreeTypeFont:
    probe = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(probe)
    fp = font_path()
    for font_size in range(size, 27, -2):
        font = ImageFont.truetype(fp, font_size)
        widest = 0
        for text in texts:
            for line in wrap_text(text, font, draw, max_width):
                widest = max(widest, draw.textbbox((0, 0), line, font=font, stroke_width=4)[2])
        if widest <= max_width:
            return font
    return ImageFont.truetype(fp, 28)


def make_overlay(path: Path, zh: str, en: str, jp: str, pos: str) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    max_width = 940

    if pos == "title":
        zh_font = fit_font([zh], 66, max_width)
        en_font = fit_font([en], 48, max_width)
        jp_font = fit_font([jp], 44, max_width)
        y = 500
    elif pos == "ending":
        zh_font = fit_font([zh], 54, max_width)
        en_font = fit_font([en], 42, max_width)
        jp_font = fit_font([jp], 40, max_width)
        y = 960
    else:
        zh_font = fit_font([zh], 52, max_width)
        en_font = fit_font([en], 40, max_width)
        jp_font = fit_font([jp], 38, max_width)
        y = 1210

    lines: list[tuple[str, ImageFont.FreeTypeFont]] = []
    for text, font in [(zh, zh_font), (en, en_font), (jp, jp_font)]:
        for line in wrap_text(text, font, draw, max_width):
            lines.append((line, font))

    heights = [draw.textbbox((0, 0), line, font=font, stroke_width=5)[3] for line, font in lines]
    total_height = sum(heights) + max(0, len(lines) - 1) * 6
    if pos == "normal":
        y = min(y, HEIGHT - total_height - 180)

    for (line, font), line_height in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=5)
        x = math.floor((WIDTH - (bbox[2] - bbox[0])) / 2)
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255), stroke_width=5, stroke_fill=(0, 0, 0, 235))
        y += line_height + 6

    img.save(path)


def read_plan() -> list[dict[str, str]]:
    with PLAN.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_srt(rows: list[dict[str, str]]) -> list[tuple[float, float, Path]]:
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)
    for old in OVERLAY_DIR.glob("*.png"):
        old.unlink()

    t = 0.0
    events: list[tuple[float, float, Path]] = []
    with SRT.open("w", encoding="utf-8") as all_srt, JP_SRT.open("w", encoding="utf-8") as jp_srt:
        for n, row in enumerate(rows, start=1):
            start = t
            end = t + float(row["duration"])
            zh, en, jp, pos = row["zh"], row["en"], row["jp"], row.get("pos", "normal")
            all_srt.write(f"{n}\n{srt_time(start)} --> {srt_time(end)}\n{zh}\n{en}\n{jp}\n\n")
            jp_srt.write(f"{n}\n{srt_time(start)} --> {srt_time(end)}\n{jp}\n\n")
            overlay = OVERLAY_DIR / f"{n:03d}.png"
            make_overlay(overlay, zh, en, jp, pos)
            events.append((start, end, overlay))
            t = end
    return events


def burn_subtitles(events: list[tuple[float, float, Path]], rows: list[dict[str, str]]) -> None:
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", str(BASE_VIDEO)]
    for _, _, image_path in events:
        cmd.extend(["-loop", "1", "-i", str(image_path)])

    current = "[0:v]"
    chain = []
    for i, (start, end, _) in enumerate(events, start=1):
        out = f"[v{i}]"
        chain.append(f"{current}[{i}:v]overlay=0:0:enable='between(t,{start:.3f},{end:.3f})'{out}")
        current = out
    subscribe_starts = [
        start for (start, _, _), row in zip(events, rows)
        if "订阅" in row.get("zh", "") or "subscribe" in row.get("en", "").lower()
    ]
    audio_map = "0:a:0?"
    if subscribe_starts:
        ding_inputs = []
        base_audio = "[0:a:0]"
        for i, start in enumerate(subscribe_starts):
            ding_start = start + 1.5
            duck_start = ding_start - 0.10
            duck_end = ding_start + 2.20
            delay_ms = int(round(ding_start * 1000))
            base_label = f"[base{i}]"
            label = f"[ding{i}]"
            main_label = f"[dingmain{i}]"
            hit_label = f"[dinghit{i}]"
            chain.append(
                f"{base_audio}volume=volume=0.30:"
                f"enable='between(t,{duck_start:.3f},{duck_end:.3f})'{base_label}"
            )
            base_audio = base_label
            chain.append(
                "sine=frequency=2800:duration=2.00:sample_rate=48000,"
                "afade=t=in:st=0:d=0.02,"
                f"afade=t=out:st=0.35:d=1.65{main_label}"
            )
            chain.append(
                "sine=frequency=5600:duration=0.25:sample_rate=48000,"
                "afade=t=in:st=0:d=0.01,"
                f"afade=t=out:st=0.08:d=0.17{hit_label}"
            )
            chain.append(
                f"{main_label}{hit_label}"
                "amix=inputs=2:duration=longest:dropout_transition=0,"
                f"adelay={delay_ms}|{delay_ms},volume=1.995{label}"
            )
            ding_inputs.append(label)
        audio_map = "[aout]"
        chain.append(
            f"{base_audio}{''.join(ding_inputs)}"
            f"amix=inputs={len(ding_inputs) + 1}:duration=first:dropout_transition=0[aout]"
        )
    filter_complex = ";".join(chain)
    FILTER_FILE.write_text(filter_complex, encoding="utf-8")

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", current,
        "-map", audio_map,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        "-shortest",
        str(FINAL_VIDEO),
    ])
    subprocess.run(cmd, check=True)


def main() -> None:
    rows = read_plan()
    events = write_srt(rows)
    burn_subtitles(events, rows)


if __name__ == "__main__":
    main()
'''


PLAN_TEMPLATE = """idx\tsrc\tstart\tduration\tzh\ten\tjp\tpos\n"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dish", help="Dish name; also used as output directory and file prefix")
    parser.add_argument("--workdir", default=".", help="Directory containing raw footage")
    args = parser.parse_args()

    workdir = Path(args.workdir).expanduser().resolve()
    out_dir = workdir / args.dish
    project = out_dir / "project"
    project.mkdir(parents=True, exist_ok=True)
    (out_dir / "analysis_frames").mkdir(exist_ok=True)

    build = project / "build_video.sh"
    render = project / "render_subtitles.py"
    plan = project / "clip_plan.tsv"

    build.write_text(BUILD_VIDEO.replace("{dish}", args.dish), encoding="utf-8")
    build.chmod(0o755)
    render.write_text(RENDER_SUBTITLES.replace("{dish}", args.dish), encoding="utf-8")
    if not plan.exists():
        plan.write_text(PLAN_TEMPLATE, encoding="utf-8")

    print(f"Created project scaffold: {out_dir}")
    print(f"Edit plan: {plan}")
    print(f"Render with: bash '{build}'")


if __name__ == "__main__":
    main()
