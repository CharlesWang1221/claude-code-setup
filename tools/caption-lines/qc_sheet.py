#!/usr/bin/env python3
"""字幕抽格聯絡表：每行字幕的中間時間點各抽一格（只裁字幕區），拼成一張圖給人眼檢查。

用法：python3 tools/caption-lines/qc_sheet.py <caption-timing.json> <影片檔樣式> <輸出資料夾>
  影片檔樣式用 {day} 代表 mon…sat，例如 renders/s4ep2-{day}-captioned-v9.mp4

看圖時逐格確認：只有 1 個框、框內只有 1 排字、文字與 TXT 相同、橘框只在 ★ 行。
"""
import json
import subprocess
import sys
from pathlib import Path


def main(timing, pattern, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for day, v in json.loads(Path(timing).read_text()).items():
        frames = []
        for i, ln in enumerate(v['lines'], 1):
            f = out / f'{day}-{i:02}.png'
            t = (ln['start'] + ln['end']) / 2
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', pattern.format(day=day),
                            '-frames:v', '1', '-vf', 'crop=1080:420:0:1140,scale=360:-1', str(f)], check=True)
            frames.append(f)
        rows = (len(frames) + 3) // 4
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-pattern_type', 'glob', '-i', str(out / f'{day}-*.png'),
                        '-vf', f'tile=4x{rows}:padding=4', '-frames:v', '1', str(out / f'sheet-{day}.png')], check=True)
        print(out / f'sheet-{day}.png')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
