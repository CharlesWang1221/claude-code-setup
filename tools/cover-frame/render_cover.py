#!/usr/bin/env python3
"""句剪專屬封面：唯一合法的產生方式。

把 skills/podcast-teaser-video/assets/cover-frame-template.html 填好欄位，用 Chrome 無頭模式截成
1080 × 1920 PNG，並輸出 IG 格狀牆 3:4 檢查縮圖。版面、字級、色碼都鎖在樣板裡，這支工具不提供
任何調整版面的參數；要改設計只能改樣板並重新送阿維核准。

用法：
  python3 tools/cover-frame/render_cover.py <covers.json> <輸出資料夾> [--shots <影片劇情圖資料夾> ...]

covers.json：
  [{"day": "mon", "art": "art/mon-cover-art.png", "tag": "S4EP2",
    "line1": "全家精神狀況", "highlight": "很脆弱", "font": "Noto Sans TC",
    "angle": "high-angle", "shot1_angle": "eye-level",
    "shots": ["shots/mon-shot-01.png", "shots/mon-shot-02.png", "shots/mon-shot-03.png", "shots/mon-shot-04.png"]}]
  art、shots 為相對 covers.json 的路徑。angle／shot1_angle 用來檢查封面角度規則。

封面不得重複使用影片內的圖片（含裁切、放大、翻轉、換角度重出同一畫面）：
- 封面畫面與任何一張劇情圖（各支 shots 加 --shots 資料夾內所有圖）位元相同，直接拒絕產出。
- 裁切與重繪無法用程式可靠判斷（2026-11-02 實測：水墨畫風讓無關圖的相似度高過裁切圖），
  所以每支另產 <day>-cover-vs-shots.png：左邊封面畫面、右邊 4 張劇情圖，交鐵雄目視。
"""
import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATE = REPO / 'skills/podcast-teaser-video/assets/cover-frame-template.html'
FONTS = {'Noto Sans TC', 'Noto Serif TC', 'Huninn', 'LXGW WenKai TC', 'Zhi Mang Xing'}
ANGLES = {'low-angle', 'high-angle', 'birds-eye', 'dutch', 'worms-eye'}  # 平視（eye-level）不得用在封面


def chrome():
    for c in (os.environ.get('CHROME'), shutil.which('google-chrome'), shutil.which('chromium'),
              '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
              r'C:\Program Files\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'):
        if c and Path(c).exists():
            return c
    sys.exit('找不到 Chrome；請設定環境變數 CHROME 指向 chrome 執行檔')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check(item, shot_hashes):
    errs = []
    for k in ('day', 'art', 'tag', 'line1', 'highlight', 'angle', 'shot1_angle', 'shots'):
        if not item.get(k):
            errs.append(f'缺欄位 {k}')
    if item.get('tag') and not re.fullmatch(r'S\d+EP\d+', item['tag']):
        errs.append(f'期別標籤「{item["tag"]}」只能放集數（例 S4EP3），不寫週幾金句或預告（2026-11-12）')
    hl = item.get('highlight', '')
    if not 2 <= len(hl) <= 4:
        errs.append(f'重點字「{hl}」須 2～4 字')
    if len(item.get('line1', '')) > 6:
        errs.append(f'主標第一行「{item.get("line1")}」超過 6 字，125 px＋字距 .07em 會折行（2026-11-12）')
    if item.get('font', 'Noto Sans TC') not in FONTS:
        errs.append(f'字型 {item.get("font")} 不在 DESIGN.md 封面字體表')
    if item.get('angle') not in ANGLES:
        errs.append(f'封面角度 {item.get("angle")} 不合規；只能用 {sorted(ANGLES)}，平視不得用在封面')
    if item.get('angle') == item.get('shot1_angle'):
        errs.append('封面角度不得與影片第 1 張相同')
    if len(item.get('shot_paths', [])) != 4:
        errs.append('shots 須列出該支 4 張劇情圖')
    missing = [p for p in item.get('shot_paths', []) if not Path(p).exists()]
    if missing:
        errs.append(f'找不到劇情圖 {missing}')
    hashes = shot_hashes | {sha(p) for p in item.get('shot_paths', []) if Path(p).exists()}
    if item.get('art_path') and sha(item['art_path']) in hashes:
        errs.append('封面畫面就是影片內的圖；封面不得重複使用影片圖片，要由大千另行出圖')
    return errs


def render(item, out_dir, exe, preview=False):
    tpl = re.sub(r'<!--.*?-->', '', TEMPLATE.read_text(encoding='utf-8'), flags=re.S)
    fill = {'{{ART}}': Path(item['art_path']).resolve().as_uri(), '{{TAG}}': html.escape(item['tag']),
            '{{LINE1}}': html.escape(item['line1']), '{{HIGHLIGHT}}': html.escape(item['highlight']),
            '{{FONT}}': html.escape(item.get('font', 'Noto Sans TC'))}
    for k, v in fill.items():
        tpl = tpl.replace(k, v)
    assert '{{' not in tpl, '樣板仍有未填欄位'
    out = out_dir / f'{item["day"]}-cover{"-PREVIEW" if preview else ""}.png'
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / 'cover.html'
        page.write_text(tpl, encoding='utf-8')
        subprocess.run([exe, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                        '--force-device-scale-factor=1', '--window-size=1080,1920', '--virtual-time-budget=8000',
                        f'--user-data-dir={td}/profile', f'--screenshot={out}', page.as_uri()],
                       check=True, capture_output=True)
    thumb = out_dir / f'{item["day"]}-cover-grid-check.png'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-vf', 'crop=1080:1440:0:240,scale=264:-1', str(thumb)],
                   check=True)
    if preview:
        return out, thumb, None
    sheet = out_dir / f'{item["day"]}-cover-vs-shots.png'
    ins = [item['art_path']] + item['shot_paths']
    args = ['ffmpeg', '-v', 'error', '-y']
    for p in ins:
        args += ['-i', p]
    fc = ''.join(f'[{i}]scale=300:534:force_original_aspect_ratio=decrease,pad=300:534:(ow-iw)/2:(oh-ih)/2:white'
                 f'{",drawbox=0:0:300:534:yellow:8" if i == 0 else ""}[v{i}];' for i in range(5))
    fc += ''.join(f'[v{i}]' for i in range(5)) + 'hstack=5'
    subprocess.run(args + ['-filter_complex', fc, str(sheet)], check=True)
    return out, thumb, sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('out_dir')
    ap.add_argument('--shots', action='append', default=[])
    ap.add_argument('--preview', action='store_true',
                    help='只給老查看樣板改版後的樣式：免填角度與劇情圖，輸出檔名帶 PREVIEW，不得當交件封面上架')
    a = ap.parse_args()
    spec = Path(a.spec)
    items = json.loads(spec.read_text(encoding='utf-8'))
    shot_hashes = {sha(p) for d in a.shots for p in Path(d).rglob('*') if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')}
    out_dir = Path(a.out_dir).resolve()  # Chrome 的 --screenshot 不認相對路徑（Windows 實測）
    out_dir.mkdir(parents=True, exist_ok=True)
    bad = False
    for it in items:
        it['art_path'] = str((spec.parent / it['art']).resolve()) if it.get('art') else ''
        it['shot_paths'] = [str((spec.parent / p).resolve()) for p in it.get('shots', [])]
        if it['art_path'] and not Path(it['art_path']).exists():
            print(f'FAIL {it.get("day")}：找不到封面畫面 {it["art"]}')
            bad = True
            continue
        errs = check(it, shot_hashes)
        if a.preview:  # 預覽只保留文字規則；角度、劇情圖、重複用圖檢查留給正式交件
            errs = [e for e in errs if not any(k in e for k in ('angle', '角度', 'shots', '劇情圖', '影片內的圖'))]
        if errs:
            bad = True
            print(f'FAIL {it.get("day")}：' + '；'.join(errs))
            continue
        out, thumb, sheet = render(it, out_dir, chrome(), a.preview)
        if a.preview:
            print(f'PREVIEW {it["day"]}：{out}（格狀牆縮圖 {thumb.name}）；僅供看樣式，不得上架')
            continue
        print(f'OK   {it["day"]}：{out}（格狀牆縮圖 {thumb.name}；對照圖 {sheet.name} 交鐵雄確認不是影片圖的裁切或重繪）')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
