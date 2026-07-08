#!/usr/bin/env python3
"""
Pexels B-roll 自動抓取器
用法: python fetch_broll.py --srt input.srt --output-dir ./04-broll/ --api-key YOUR_KEY --count 5
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path


PEXELS_VIDEO_API = "https://api.pexels.com/videos/search"


def load_env(start_path: str = None) -> None:
    """往上找 .env 檔，載入 key=value 進環境變數（不覆蓋已有的值）。"""
    search = Path(start_path or __file__).resolve()
    for parent in [search] + list(search.parents):
        env_file = parent / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip()
            return


load_env()

STOP_WORDS = {
    "的", "了", "是", "在", "我", "你", "他", "她", "它", "們",
    "有", "和", "就", "不", "也", "都", "而", "及", "與", "或",
    "but", "the", "and", "is", "in", "to", "a", "an", "of", "for",
    "this", "that", "it", "we", "you", "they", "with", "at", "from",
}


def parse_srt(srt_path: str) -> list[dict]:
    with open(srt_path, encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\n+", content.strip())
    subtitles = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        try:
            index = int(lines[0])
        except ValueError:
            continue
        time_match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", lines[1])
        if not time_match:
            continue
        text = " ".join(lines[2:])
        subtitles.append({
            "index": index,
            "start": lines[1].split(" --> ")[0],
            "end": lines[1].split(" --> ")[1],
            "text": text,
        })
    return subtitles


def extract_keywords(subtitles: list[dict], top_n: int = 10) -> list[str]:
    all_text = " ".join(s["text"] for s in subtitles)
    # Simple word frequency
    words = re.findall(r"[一-鿿]{2,}|[a-zA-Z]{4,}", all_text)
    filtered = [w for w in words if w.lower() not in STOP_WORDS]
    freq = Counter(filtered)
    return [word for word, _ in freq.most_common(top_n)]


def time_to_seconds(time_str: str) -> float:
    parts = time_str.replace(",", ".").split(":")
    h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
    return h * 3600 + m * 60 + s


def search_pexels_video(keyword: str, api_key: str, per_page: int = 3) -> list[dict]:
    from urllib.parse import quote
    url = f"{PEXELS_VIDEO_API}?query={quote(keyword)}&per_page={per_page}&size=medium"
    req = urllib.request.Request(url, headers={
        "Authorization": api_key,
        "User-Agent": "Mozilla/5.0 (compatible; BrollFetcher/1.0)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    videos = []
    for v in data.get("videos", []):
        # Pick 720p or the closest available
        files = sorted(v.get("video_files", []), key=lambda f: abs(f.get("height", 0) - 720))
        if files:
            videos.append({
                "id": v["id"],
                "url": files[0]["link"],
                "width": files[0].get("width"),
                "height": files[0].get("height"),
                "duration": v.get("duration"),
            })
    return videos


def download_video(url: str, dest_path: str) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())


def pick_broll_timestamps(subtitles: list[dict], count: int) -> list[dict]:
    """Pick evenly spaced subtitle blocks for B-roll insertion."""
    if not subtitles or count <= 0:
        return []
    step = max(1, len(subtitles) // (count + 1))
    picked = []
    for i in range(step, len(subtitles), step):
        if len(picked) >= count:
            break
        picked.append(subtitles[i])
    return picked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--srt", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--api-key", default=os.environ.get("PEXELS_API_KEY"))
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--keywords", help="逗號分隔的英文關鍵字，一對一覆蓋自動擷取（如：security camera,stressed woman,family worried）")
    args = parser.parse_args()

    if not args.api_key:
        raise SystemExit("ERROR: 需要 PEXELS_API_KEY — 到 https://www.pexels.com/api/ 申請")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("[1/4] 解析 SRT...")
    subtitles = parse_srt(args.srt)
    if not subtitles:
        raise SystemExit("ERROR: SRT 解析失敗，請確認格式正確")
    print(f"   共 {len(subtitles)} 段字幕")

    print("[2/4] 擷取關鍵字...")
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
        print(f"   使用手動關鍵字：{', '.join(keywords)}")
    else:
        keywords = extract_keywords(subtitles, top_n=args.count * 2)
        print(f"   關鍵字：{', '.join(keywords[:args.count])}")

    target_blocks = pick_broll_timestamps(subtitles, args.count)

    broll_list = []
    for i, (keyword, block) in enumerate(zip(keywords[:args.count], target_blocks)):
        print(f"\n[3/4] [{i+1}/{args.count}] 搜尋「{keyword}」...")
        try:
            results = search_pexels_video(keyword, args.api_key, per_page=3)
            if not results:
                print(f"   找不到結果，跳過")
                continue
            video = results[0]
            filename = f"broll_{i+1:02d}_{keyword[:10]}.mp4"
            dest = out_dir / filename
            print(f"   下載 {video['width']}x{video['height']} ({video['duration']}s)...")
            download_video(video["url"], str(dest))
            broll_list.append({
                "file": filename,
                "keyword": keyword,
                "insert_at_seconds": time_to_seconds(block["start"]),
                "insert_at_subtitle_index": block["index"],
                "subtitle_text": block["text"],
                "pexels_id": video["id"],
            })
            print(f"   OK: {filename}")
        except Exception as e:
            print(f"   FAIL: {e}")

    list_path = out_dir / "broll_list.json"
    with open(list_path, "w", encoding="utf-8") as f:
        json.dump(broll_list, f, ensure_ascii=False, indent=2)
    print(f"\n[4/4] 完成！共下載 {len(broll_list)} 個 B-roll")
    print(f"   清單：{list_path}")


if __name__ == "__main__":
    main()
