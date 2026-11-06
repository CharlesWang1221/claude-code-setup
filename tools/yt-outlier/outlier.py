#!/usr/bin/env python3
"""Compare public YouTube videos against their own channel and format median."""
import argparse
import concurrent.futures
import datetime as dt
import json
import pathlib
import statistics
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHANNELS = pathlib.Path(__file__).with_name('channels.txt')


def fetch(args):
    command = [sys.executable, '-m', 'yt_dlp', '--ignore-config', '--no-cookies', '--no-warnings', '--skip-download', *args]
    try:
        return subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 1, '', '讀取逾時（90 秒）')


def channels():
    for number, line in enumerate(CHANNELS.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) != 3 or parts[2] not in ('tw', 'intl', 'self'):
            raise ValueError(f'channels.txt line {number}: expected name, URL, tw/intl/self separated by tabs')
        yield parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=20)
    parser.add_argument('--min', type=float, default=2.0, dest='minimum')
    args = parser.parse_args()
    if args.limit < 1 or args.minimum < 0:
        parser.error('--limit must be positive and --min must be nonnegative')
    started = time.monotonic()
    report = {'generated_at': dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat(), 'limit': args.limit, 'minimum': args.minimum, 'results': [], 'skipped': [], 'reference': []}
    for name, url, group in channels():
        for tab, label in [('videos', '長片'), ('shorts', 'Shorts')]:
            print(f'{name} / {label}', flush=True)
            if url == 'N/A':
                report['skipped'].append({'channel': name, 'format': label, 'reason': '未找到官方頻道網址'})
                continue
            listing = fetch(['--flat-playlist', '--playlist-end', str(args.limit), '--print', 'id', url.rstrip('/') + '/' + tab])
            if listing.returncode:
                err = listing.stderr.strip().splitlines()
                reason = '該頻道沒有此分頁' if 'does not have a' in listing.stderr and 'tab' in listing.stderr else ('清單讀取失敗：' + (err[-1] if err else '未知錯誤'))
                report['skipped'].append({'channel': name, 'format': label, 'reason': reason})
                continue
            ids = list(dict.fromkeys(x.strip() for x in listing.stdout.splitlines() if x.strip()))
            videos, failures = [], 0
            def read_video(video_id):
                video_url = 'https://www.youtube.com/watch?v=' + video_id
                return fetch(['--no-playlist', '--dump-single-json', video_url])
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                items = list(pool.map(read_video, ids))
            for video_id, item in zip(ids, items):
                video_url = 'https://www.youtube.com/watch?v=' + video_id
                try:
                    data = json.loads(item.stdout)
                    views = data.get('view_count') if isinstance(data, dict) else None
                    if item.returncode or not isinstance(views, int) or views < 0:
                        raise ValueError('missing view count')
                    videos.append({'channel': name, 'group': group, 'format': label, 'title': data.get('title') or video_id, 'url': video_url, 'views': views})
                except (ValueError, json.JSONDecodeError):
                    failures += 1
            if failures:
                report['skipped'].append({'channel': name, 'format': label, 'reason': f'{failures} 支影片資料讀取失敗；中位數僅依成功讀取的影片計算'})
            if len(videos) < 4:
                report['skipped'].append({'channel': name, 'format': label, 'reason': f'有效影片 {len(videos)} 支，少於 4 支'})
                continue
            median = statistics.median(v['views'] for v in videos)
            if median <= 0:
                report['skipped'].append({'channel': name, 'format': label, 'reason': '播放數中位數為 0，無法計算倍數'})
                continue
            for video in videos:
                video.update(median=median, multiple=video['views'] / median)
                if group == 'self':
                    report['reference'].append(video)
                elif video['multiple'] >= args.minimum:
                    report['results'].append(video)
    report['results'].sort(key=lambda x: x['multiple'], reverse=True)
    report['reference'].sort(key=lambda x: x['multiple'], reverse=True)
    report['elapsed_seconds'] = round(time.monotonic() - started, 1)
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
    monday = today - dt.timedelta(days=today.weekday())
    out = ROOT / 'output' / 'weekly-shorts' / monday.isoformat()
    out.mkdir(parents=True, exist_ok=True)
    (out / 'outlier-radar.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = [f'# 競品爆款雷達 {monday}', '', f'門檻 {args.minimum:g} 倍；每格式最多 {args.limit} 支；耗時 {report["elapsed_seconds"]} 秒。', '', '## 達門檻影片', '', '| 倍數 | 播放數 | 中位數 | 頻道 | 標題 | 格式 |', '| ---: | ---: | ---: | --- | --- | --- |']
    for v in report['results']:
        title = v['title'].replace('|', '｜').replace('\n', ' ')
        lines.append(f'| {v["multiple"]:.2f} | {v["views"]:,} | {v["median"]:,.0f} | {v["channel"]} | [{title}]({v["url"]}) | {v["format"]} |')
    lines += ['', '## 跳過與資料缺漏', '']
    lines += [f'- {s["channel"]} / {s["format"]}：{s["reason"]}' for s in report['skipped']] or ['- 無']
    lines += ['', '## 我方參照', '']
    lines += [f'- {v["format"]}：[{v["title"]}]({v["url"]})，{v["views"]:,} 次，中位數 {v["median"]:,.0f}，{v["multiple"]:.2f} 倍' for v in report['reference']] or ['- 無可計算資料']
    (out / 'outlier-radar.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'完成：{out}，{report["elapsed_seconds"]} 秒', flush=True)


if __name__ == '__main__':
    main()
