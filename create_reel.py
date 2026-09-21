#!/usr/bin/env python3
"""
Marine Radar — Social Media Reel Generator

Creates split-screen reels (portrait) for Instagram Reels / TikTok / YouTube Shorts.

Layout (1080x2160):
    ┌────────────────────┐
    │                    │
    │   Stock Footage    │  1080x1080 (cropped to square)
    │                    │
    │ ▓▓▓ TEXT BAR ▓▓▓▓▓ │  1080x140 (overlaid on bottom of stock footage)
    ├────────────────────┤
    │                    │
    │  Marine Radar      │  1080x1080 (untouched)
    │  Route Recording   │
    │                    │
    └────────────────────┘

Usage:
    python create_reel.py --stock stock.mp4 --recording recording.mp4 --vessel "MSC CAROUGE"
    python create_reel.py --stock stock.mp4 --recording recording.mp4 --vessel "EVER GIVEN" --duration 12

Requirements:
    pip install Pillow
    brew install ffmpeg
"""

import argparse
import os
import subprocess
import shutil
import sys
from PIL import Image, ImageDraw, ImageFont


# ── Settings ───────────────────────────────────────────────────────────────

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".temp")
BAR_WIDTH = 1080
BAR_HEIGHT = 140


# ── Text Bar Generator ────────────────────────────────────────────────────

def create_text_bar(vessel_name: str, output_path: str):
    """Create the center text bar image."""
    img = Image.new("RGB", (BAR_WIDTH, BAR_HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    line1 = f"{vessel_name} Vessel Recap"
    line2 = 'Comment "app" to get yours'

    try:
        font1 = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42)
        font2 = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except OSError:
        font1 = ImageFont.load_default(42)
        font2 = ImageFont.load_default(30)

    bbox1 = draw.textbbox((0, 0), line1, font=font1)
    x1 = (BAR_WIDTH - (bbox1[2] - bbox1[0])) // 2
    draw.text((x1, 25), line1, fill="white", font=font1)

    bbox2 = draw.textbbox((0, 0), line2, font=font2)
    x2 = (BAR_WIDTH - (bbox2[2] - bbox2[0])) // 2
    draw.text((x2, 80), line2, fill="#cccccc", font=font2)

    img.save(output_path)


# ── Video Composer ─────────────────────────────────────────────────────────

def compose_reel(stock_path: str, recording_path: str, vessel_name: str,
                 output_path: str, duration: int):
    """Compose the split-screen reel using FFmpeg."""
    if not shutil.which("ffmpeg"):
        print("ERROR: ffmpeg not found. Install with: brew install ffmpeg")
        sys.exit(1)

    os.makedirs(TEMP_DIR, exist_ok=True)
    bar_path = os.path.join(TEMP_DIR, "text_bar.png")
    create_text_bar(vessel_name, bar_path)

    # Get recording duration to cap output
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format",
         recording_path],
        capture_output=True, text=True
    )
    import json
    rec_duration = float(json.loads(probe.stdout)["format"]["duration"])
    final_duration = min(duration, int(rec_duration))

    # Pick a start point in the middle of the stock footage for best content
    stock_probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format",
         stock_path],
        capture_output=True, text=True
    )
    stock_duration = float(json.loads(stock_probe.stdout)["format"]["duration"])
    stock_start = max(0, (stock_duration - final_duration) / 2)

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(stock_start), "-t", str(final_duration), "-i", stock_path,
        "-t", str(final_duration), "-i", recording_path,
        "-loop", "1", "-t", str(final_duration), "-i", bar_path,
        "-filter_complex",
        "[0:v]scale=-1:1080,crop=1080:1080,setsar=1[top];"
        "[1:v]scale=1080:1080,setsar=1[bottom];"
        "[top][bottom]vstack=inputs=2[stacked];"
        "[2:v]scale=1080:140,setsar=1[bar];"
        "[stacked][bar]overlay=0:1080-120[outv]",
        "-map", "[outv]",
        "-t", str(final_duration),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-an",
        output_path,
    ]

    print(f"Composing reel: {vessel_name}")
    print(f"  Stock:     {stock_path} (starting at {stock_start:.1f}s)")
    print(f"  Recording: {recording_path}")
    print(f"  Duration:  {final_duration}s")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"FFmpeg error:\n{result.stderr[-500:]}")
        sys.exit(1)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  Output:    {output_path} ({size_mb:.1f} MB)")


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Marine Radar — Social Media Reel Generator"
    )
    parser.add_argument("--stock", "-s", required=True,
                        help="Path to stock ship video")
    parser.add_argument("--recording", "-r", required=True,
                        help="Path to Marine Radar route recording")
    parser.add_argument("--vessel", "-v", required=True,
                        help="Vessel name (e.g. 'MSC CAROUGE')")
    parser.add_argument("--output", "-o", default=None,
                        help="Output file path (auto-generated if not set)")
    parser.add_argument("--duration", "-d", type=int, default=15,
                        help="Max output duration in seconds (default: 15)")

    args = parser.parse_args()

    if not os.path.isfile(args.stock):
        parser.error(f"Stock video not found: {args.stock}")
    if not os.path.isfile(args.recording):
        parser.error(f"Recording not found: {args.recording}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output = args.output or os.path.join(
        OUTPUT_DIR,
        f"reel_{args.vessel.replace(' ', '_')}.mp4"
    )

    compose_reel(args.stock, args.recording, args.vessel, output, args.duration)
    print("Done!")


if __name__ == "__main__":
    main()
