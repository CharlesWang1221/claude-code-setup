#!/usr/bin/env python3
"""
Whisper 字幕轉錄
用法: python transcribe.py --video input.mp4 --output-dir ./02-transcript/ [--model medium] [--language zh]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model", default="medium", choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--language", default="zh")
    args = parser.parse_args()

    video_path = Path(args.video)
    if not video_path.exists():
        raise SystemExit(f"ERROR: 找不到影片 {args.video}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    srt_path = out_dir / (video_path.stem + ".srt")

    print(f"🎤 開始轉錄：{video_path.name}")
    print(f"   模型：{args.model}，語言：{args.language}")
    print(f"   輸出：{srt_path}")

    cmd = [
        sys.executable, "-m", "whisper",
        str(video_path),
        "--model", args.model,
        "--language", args.language,
        "--output_format", "srt",
        "--output_dir", str(out_dir),
    ]

    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        raise SystemExit("ERROR: Whisper 執行失敗，請確認 `pip install openai-whisper` 已安裝")

    if srt_path.exists():
        lines = srt_path.read_text(encoding="utf-8").count("\n\n")
        print(f"✅ 轉錄完成，共約 {lines} 段字幕：{srt_path}")
    else:
        print("⚠ 轉錄完成但找不到 SRT，請手動確認")


if __name__ == "__main__":
    main()
