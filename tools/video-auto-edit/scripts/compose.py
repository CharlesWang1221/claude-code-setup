#!/usr/bin/env python3
"""
最終合成：三區式版型 / 自拍風版型
用法: python compose.py --video edited.mp4 --srt input.srt --title "標題" --cta "追蹤我" --output final.mp4 [--layout three-zone|selfie]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


# 三區式尺寸（1080x1920 垂直）
CANVAS_W = 1080
CANVAS_H = 1920
TITLE_ZONE_H = 280      # 上：標題區
VIDEO_ZONE_Y = 280      # 中：影片起始 Y
VIDEO_ZONE_H = 1200     # 中：影片高度
CTA_ZONE_Y = 1520       # 下：CTA 文字 Y


def run_ffmpeg(args_list: list, desc: str = ""):
    cmd = ["ffmpeg", "-y"] + args_list
    if desc:
        print(f"  ▶ {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("FFmpeg stderr:", result.stderr[-2000:])
        raise RuntimeError(f"FFmpeg 失敗：{desc}")


def get_video_duration(video_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
        capture_output=True, text=True
    )
    info = json.loads(result.stdout)
    return float(info["format"]["duration"])


def _safe_path(p: str) -> str:
    """Copy file to a temp path without spaces if needed; return safe path."""
    import shutil
    if " " not in p:
        return p
    ext = Path(p).suffix
    tmp = Path(tempfile.mkdtemp()) / ("file" + ext)
    shutil.copy2(p, tmp)
    return str(tmp)


def compose_three_zone(video: str, srt: str, title: str, cta: str, output: str):
    """
    三區式版型：
    - 黑底 1080×1920
    - 上：標題文字（置中）
    - 中：主影片（縮放至 1080×1200，含 SRT 字幕）
    - 下：CTA 文字（置中）
    """
    # Scale: fit video into 1080×VIDEO_ZONE_H with letterbox
    vid_scale = f"scale={CANVAS_W}:{VIDEO_ZONE_H}:force_original_aspect_ratio=decrease,pad={CANVAS_W}:{VIDEO_ZONE_H}:(ow-iw)/2:(oh-ih)/2"

    subtitle_style = "FontName=Noto Sans TC,FontSize=24,PrimaryColour=&Hffffff,OutlineColour=&H000000,Outline=2,Alignment=2,MarginV=40"

    # Escape colons for FFmpeg drawtext
    safe_title = title.replace("'", "\\'").replace(":", "\\:")
    safe_cta = cta.replace("'", "\\'").replace(":", "\\:")

    # Windows: copy files to temp if paths contain spaces
    video = _safe_path(video)

    # Write filter to a script file to handle all path edge cases
    title_file = Path(tempfile.mktemp(suffix=".txt"))
    cta_file = Path(tempfile.mktemp(suffix=".txt"))
    title_file.write_text(title, encoding="utf-8")
    cta_file.write_text(cta, encoding="utf-8")

    esc = lambda p: str(p).replace("\\", "/").replace(":", "\\:")

    # Build subtitle filter with vertical offset (shift subtitles up into video zone)
    srt_abs = esc(_safe_path(srt))

    filter_complex = (
        f"color=black:size={CANVAS_W}x{CANVAS_H}:d=999[bg];"
        f"[0:v]{vid_scale}[vid];"
        f"[vid]subtitles='{srt_abs}':force_style='{subtitle_style}'[vid_sub];"
        f"[bg][vid_sub]overlay=0:{VIDEO_ZONE_Y}[comp];"
        f"[comp]drawtext=text='{safe_title}':fontcolor=white:fontsize=52:x=(w-text_w)/2:y={TITLE_ZONE_H//2 - 26}:font='Noto Sans TC'[t];"
        f"[t]drawtext=text='{safe_cta}':fontcolor=white@0.85:fontsize=32:x=(w-text_w)/2:y={CTA_ZONE_Y}:font='Noto Sans TC'[final]"
    )

    run_ffmpeg([
        "-i", video,
        "-filter_complex", filter_complex,
        "-map", "[final]",
        "-map", "0:a",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output,
    ], "三區式版型合成")


def compose_selfie(video: str, srt: str, title: str, output: str):
    """
    自拍風版型：
    - 全螢幕影片（縮放至 1080×1920 填滿）
    - 頂部半透明黑色遮罩壓標題文字
    - SRT 字幕燒入
    """
    subtitle_style = "FontName=Noto Sans TC,FontSize=28,PrimaryColour=&Hffffff,OutlineColour=&H000000,Outline=3,Alignment=2,MarginV=160"

    srt_abs = str(Path(srt).resolve()).replace("\\", "/").replace(":", "\\:")
    safe_title = title.replace("'", "\\'").replace(":", "\\:")

    filter_complex = (
        f"[0:v]scale={CANVAS_W}:{CANVAS_H}:force_original_aspect_ratio=increase,crop={CANVAS_W}:{CANVAS_H}[vid];"
        f"[vid]subtitles='{srt_abs}':force_style='{subtitle_style}'[vid_sub];"
        f"[vid_sub]drawbox=x=0:y=0:w={CANVAS_W}:h=200:color=black@0.6:t=fill[boxed];"
        f"[boxed]drawtext=text='{safe_title}':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=80:font='Noto Sans TC'[final]"
    )

    run_ffmpeg([
        "-i", video,
        "-filter_complex", filter_complex,
        "-map", "[final]",
        "-map", "0:a",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        output,
    ], "自拍風版型合成")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--srt", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--cta", default="")
    parser.add_argument("--broll-list", default=None)
    parser.add_argument("--output", required=True)
    parser.add_argument("--layout", default="three-zone", choices=["three-zone", "selfie"])
    args = parser.parse_args()

    for path in [args.video, args.srt]:
        if not Path(path).exists():
            raise SystemExit(f"ERROR: 找不到 {path}")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    print(f"🎬 合成版型：{args.layout}")
    print(f"   影片：{args.video}")
    print(f"   字幕：{args.srt}")
    print(f"   標題：{args.title}")

    if args.layout == "three-zone":
        compose_three_zone(args.video, args.srt, args.title, args.cta, args.output)
    elif args.layout == "selfie":
        compose_selfie(args.video, args.srt, args.title, args.output)

    print(f"\n✅ 成品：{args.output}")


if __name__ == "__main__":
    main()
