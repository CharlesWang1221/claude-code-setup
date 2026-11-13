#!/usr/bin/env python3
"""句剪專屬封面：唯一合法的產生方式。

把 skills/podcast-teaser-video/assets/cover-frame-template.html 填好欄位，用 Chrome 無頭模式截成
1080 × 1920 PNG，並輸出 IG 格狀牆 3:4 檢查縮圖。版面、字級、色碼都鎖在樣板裡，這支工具不提供
任何調整版面的參數；要改設計只能改樣板並重新送阿維核准。

用法：
  python3 tools/cover-frame/render_cover.py <covers.json> <輸出資料夾> [--shots <影片劇情圖資料夾> ...]

covers.json：
  [{"day": "mon", "art": "art/mon-cover-art.png", "tag": "S4EP2｜週一預告",
    "line1": "全家精神狀況", "highlight": "很脆弱", "font": "Noto Sans TC",
    "angle": "high-angle", "shot1_angle": "eye-level",
    "shots": ["shots/mon-shot-01.png", "shots/mon-shot-02.png", "shots/mon-shot-03.png", "shots/mon-shot-04.png"]}]
  art、shots 為相對 covers.json 的路徑。angle／shot1_angle 用來檢查封面角度規則。

字型（2026-11-09 起，離線、可驗證）：
- 不再連 Google Fonts。工具在本機字型資料夾找 .ttf／.otf（macOS ~/Library/Fonts、/Library/Fonts、
  /System/Library/Fonts；Windows 使用者與系統 Fonts；Linux ~/.local/share/fonts、/usr/share/fonts），
  或環境變數 COVER_FONT_DIR 指定的資料夾（可用 os.pathsep 分隔多個；字型檔不得放進公開 repo）。
- 檔名須以字族名去空白開頭，例：NotoSansTC-VariableFont_wght.ttf、NotoSansTC-Black.ttf、
  NotoSerifTC-Black.ttf、Huninn-Regular.ttf、LXGWWenKaiTC-Bold.ttf、ZhiMangXing-Regular.ttf。
  有可變字型優先用；否則選最接近需求字重（標籤／節目名 700、主標 900）的靜態檔。
- 找不到字型、字型缺任何一個要顯示的字（讀 cmap 表）、Chrome 回報字型未載入，一律不產圖。
- Chrome 以 --host-resolver-rules 封鎖網路，確保離線也是同一張圖。

版位驗證：先用 Chrome 量測一次（--dump-dom），期別標籤、主標（含重點字色塊）、節目名的外框與實際文字
範圍都必須在 x 76–1004 內，且全部落在 y 280–860 的文字留白帶（大千封面畫面在這段不畫角色頭部）：
期別標籤與主標（含色塊）底緣不低於 y 720，節目名在 y 730–860（主標正下方）。任一越界就不截圖。
2026-11-09 v4 起節目名不再放畫面下方（舊版 y 1410–1510 壓到人物臉與眼睛，阿維複審 REVISE）。

封面不得重複使用影片內的圖片（含裁切、放大、翻轉、換角度重出同一畫面）：
- 封面畫面與任何一張劇情圖（各支 shots 加 --shots 資料夾內所有圖）位元相同，直接拒絕產出。
- 裁切與重繪無法用程式可靠判斷（2026-11-02 實測：水墨畫風讓無關圖的相似度高過裁切圖），
  所以每支另產 <day>-cover-vs-shots.png：左邊封面畫面、右邊 4 張劇情圖，交鐵雄目視。
"""
import argparse
import functools
import hashlib
import html
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TEMPLATE = REPO / 'skills/podcast-teaser-video/assets/cover-frame-template.html'
FONTS = {'Noto Sans TC', 'Noto Serif TC', 'Huninn', 'LXGW WenKai TC', 'Zhi Mang Xing'}
BASE_FONT = 'Noto Sans TC'   # 期別標籤與節目名固定字型
SHOW_NAME = '不標準答案'      # 與樣板 .show 內文一致
ANGLES = {'low-angle', 'high-angle', 'birds-eye', 'dutch', 'worms-eye'}  # 平視（eye-level）不得用在封面

# 版位驗證界線（SKILL.md「直式安全框」「格狀牆裁切」）
SAFE_LEFT, SAFE_RIGHT = 76, 1004
TEXT_TOP = 280          # 文字區起點：期別標籤上緣；任何文字不得高於此線
HEADLINE_BOTTOM = 720   # 期別標籤與主標（含重點字色塊）底緣
SHOW_TOP = 730          # 節目名黃框上緣下限：與主標色塊至少隔 10 px
TEXT_BOTTOM = 860       # 文字留白帶底緣＝節目名黃框底緣上限；以下留給人物，不放文字
TOL = 0.5
# 每個量測元素允許的 y 範圍（上緣下限, 底緣上限）
Y_LIMITS = {'.tag': (TEXT_TOP, HEADLINE_BOTTOM), '.headline': (TEXT_TOP, HEADLINE_BOTTOM),
            '.hl': (TEXT_TOP, HEADLINE_BOTTOM), '.show': (SHOW_TOP, TEXT_BOTTOM)}

CHROME_FLAGS = ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--allow-file-access-from-files',
                '--force-device-scale-factor=1', '--window-size=1080,1920', '--virtual-time-budget=8000',
                '--host-resolver-rules=MAP * ~NOTFOUND']

WEIGHT_WORDS = {'': 400, 'regular': 400, 'book': 400, 'normal': 400, 'thin': 100, 'hairline': 100,
                'extralight': 200, 'ultralight': 200, 'light': 300, 'demilight': 350, 'medium': 500,
                'semibold': 600, 'demibold': 600, 'bold': 700, 'extrabold': 800, 'ultrabold': 800,
                'black': 900, 'heavy': 900}

# 只在量測那一次注入；截圖用的頁面不含這段
PROBE = r'''<pre id="cover-check" style="display:none"></pre>
<script>
(async () => {
  const r = {faces: [], loads: {}, boxes: {}};
  try {
    const t = s => document.querySelector(s).textContent;
    r.loads.CoverBase = (await document.fonts.load('700 42px "CoverBase"', t('.tag') + t('.show'))).length;
    r.loads.CoverHead = (await document.fonts.load('900 125px "CoverHead"', t('.headline'))).length;
    await document.fonts.ready;
    document.fonts.forEach(f => r.faces.push({family: f.family, status: f.status}));
    for (const s of ['.tag', '.headline', '.hl', '.show']) {
      const el = document.querySelector(s);
      const a = el.getBoundingClientRect();
      const rg = document.createRange(); rg.selectNodeContents(el);
      const b = rg.getBoundingClientRect();
      r.boxes[s] = {left: Math.min(a.left, b.left), top: Math.min(a.top, b.top),
                    right: Math.max(a.right, b.right), bottom: Math.max(a.bottom, b.bottom)};
    }
  } catch (e) { r.error = String(e); }
  document.getElementById('cover-check').textContent = JSON.stringify(r);
})();
</script>
'''


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


# ---------- 本機字型 ----------

def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def font_dirs():
    ds = [Path(p) for p in os.environ.get('COVER_FONT_DIR', '').split(os.pathsep) if p]
    home = Path.home()
    ds += [home / 'Library/Fonts', Path('/Library/Fonts'), Path('/System/Library/Fonts'),
           home / '.local/share/fonts', home / '.fonts', Path('/usr/local/share/fonts'), Path('/usr/share/fonts')]
    if os.environ.get('LOCALAPPDATA'):
        ds.append(Path(os.environ['LOCALAPPDATA']) / 'Microsoft/Windows/Fonts')
    if os.environ.get('WINDIR'):
        ds.append(Path(os.environ['WINDIR']) / 'Fonts')
    return [d for d in ds if d.is_dir()]


@functools.lru_cache(maxsize=None)
def font_files():
    seen, out = set(), []
    for d in font_dirs():
        try:
            paths = list(d.rglob('*'))
        except OSError:
            continue
        for p in paths:
            try:
                if p.suffix.lower() not in ('.ttf', '.otf') or not p.is_file():
                    continue
                rp = p.resolve()
            except OSError:
                continue
            if rp not in seen:
                seen.add(rp)
                out.append((norm(p.stem), rp))
    return tuple(out)


def weight_of(rest):
    if 'italic' in rest:
        return None
    if rest.startswith('variablefont') or rest in ('vf', 'variable', 'wght'):
        return 'var'
    return WEIGHT_WORDS.get(rest)


def find_font(family, want):
    """回傳 (字型檔, @font-face font-weight 描述) 或 None。"""
    key = norm(family)
    cands = []
    for n, p in font_files():
        if n.startswith(key):
            w = weight_of(n[len(key):])
            if w is not None:
                cands.append((w, p))
    var = sorted((p for w, p in cands if w == 'var'), key=str)
    if var:
        return var[0], '100 900'
    static = [(w, p) for w, p in cands if w != 'var']
    if not static:
        return None
    w, p = min(static, key=lambda c: (abs(c[0] - want), -c[0], str(c[1])))
    return p, str(w)


def cmap_lookup(path):
    """讀 TrueType／OpenType 的 cmap 表，回傳 has(codepoint) 函式；不依賴第三方套件。"""
    data = Path(path).read_bytes()
    if data[:4] == b'ttcf':
        raise ValueError('不支援 .ttc 字型集合，請改用單一 .ttf／.otf')
    tables = {}
    for i in range(struct.unpack_from('>H', data, 4)[0]):
        tag, _, off, _ = struct.unpack_from('>4sIII', data, 12 + 16 * i)
        tables[tag] = off
    cm = tables[b'cmap']
    f12 = f4 = None
    for i in range(struct.unpack_from('>H', data, cm + 2)[0]):
        pid, eid, so = struct.unpack_from('>HHI', data, cm + 4 + 8 * i)
        if not (pid == 0 or (pid == 3 and eid in (1, 10))):
            continue
        p = cm + so
        fmt = struct.unpack_from('>H', data, p)[0]
        if fmt == 12 and f12 is None:
            f12 = p
        elif fmt == 4 and f4 is None:
            f4 = p
    if f12 is not None:
        ng = struct.unpack_from('>I', data, f12 + 12)[0]
        groups = [struct.unpack_from('>III', data, f12 + 16 + 12 * i) for i in range(ng)]
        return lambda c: any(s <= c <= e for s, e, _ in groups)
    if f4 is not None:
        seg = struct.unpack_from('>H', data, f4 + 6)[0] // 2
        ends = struct.unpack_from(f'>{seg}H', data, f4 + 14)
        starts = struct.unpack_from(f'>{seg}H', data, f4 + 16 + 2 * seg)
        deltas = struct.unpack_from(f'>{seg}h', data, f4 + 16 + 4 * seg)
        ro = f4 + 16 + 6 * seg
        offs = struct.unpack_from(f'>{seg}H', data, ro)

        def has(c):
            if c > 0xFFFF:
                return False
            for i in range(seg):
                if starts[i] <= c <= ends[i]:
                    if offs[i] == 0:
                        return (c + deltas[i]) & 0xFFFF != 0
                    g = struct.unpack_from('>H', data, ro + 2 * i + offs[i] + 2 * (c - starts[i]))[0]
                    return g != 0 and (g + deltas[i]) & 0xFFFF != 0
            return False
        return has
    raise ValueError('找不到 Unicode cmap（format 4／12）')


def resolve_fonts(item):
    errs, fonts = [], {}
    head = item.get('font', BASE_FONT)
    if head not in FONTS:
        return fonts, errs  # 字型名不合規已由 check() 報錯
    jobs = (('CoverBase', BASE_FONT, 700, item.get('tag', '') + SHOW_NAME),
            ('CoverHead', head, 900, item.get('line1', '') + item.get('highlight', '')))
    for alias, fam, want, text in jobs:
        hit = find_font(fam, want)
        if not hit:
            errs.append(f'本機找不到字型「{fam}」的 .ttf／.otf；請安裝，或設 COVER_FONT_DIR 指向字型檔資料夾（字型不得放進公開 repo）')
            continue
        path, desc = hit
        try:
            has = cmap_lookup(path)
        except Exception as e:  # noqa: BLE001 — 任何解析失敗都要擋下
            errs.append(f'無法讀取字型 {path.name} 的字元表：{e}')
            continue
        miss = [ch for ch in dict.fromkeys(text) if not ch.isspace() and not has(ord(ch))]
        if miss:
            errs.append(f'字型「{fam}」（{path.name}）缺字 {"".join(miss)}，會跑 fallback')
            continue
        fonts[alias] = (path, desc)
    return fonts, errs


# ---------- 檢查與產出 ----------

def check(item, shot_hashes):
    errs = []
    for k in ('day', 'art', 'tag', 'line1', 'highlight', 'angle', 'shot1_angle', 'shots'):
        if not item.get(k):
            errs.append(f'缺欄位 {k}')
    hl = item.get('highlight', '')
    if not 2 <= len(hl) <= 4:
        errs.append(f'重點字「{hl}」須 2～4 字')
    if len(item.get('line1', '')) > 7:
        errs.append(f'主標第一行「{item.get("line1")}」超過 7 字，125 px 會折行')
    if item.get('font', BASE_FONT) not in FONTS:
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
    fonts, ferrs = resolve_fonts(item)
    errs += ferrs
    item['fonts'] = fonts
    return errs


def build_page(item, td):
    faces = []
    copied = {}
    for alias, (path, desc) in item['fonts'].items():
        if path not in copied:
            copied[path] = f'font-{len(copied)}{path.suffix.lower()}'
            shutil.copyfile(path, Path(td) / copied[path])
        faces.append(f'  @font-face {{ font-family: "{alias}"; src: url("{copied[path]}"); '
                     f'font-weight: {desc}; font-style: normal; font-display: block; }}')
    tpl = re.sub(r'<!--.*?-->', '', TEMPLATE.read_text(encoding='utf-8'), flags=re.S)
    fill = {'{{FONT_FACES}}': '\n'.join(faces),
            '{{ART}}': Path(item['art_path']).resolve().as_uri(), '{{TAG}}': html.escape(item['tag']),
            '{{LINE1}}': html.escape(item['line1']), '{{HIGHLIGHT}}': html.escape(item['highlight'])}
    for k, v in fill.items():
        tpl = tpl.replace(k, v)
    assert '{{' not in tpl, '樣板仍有未填欄位'
    assert not re.search(r'https?://', tpl), '樣板不得引用網路資源（字型、圖片都要本機檔）'
    return tpl


def verify(probe, exe, td, fonts):
    res = subprocess.run([exe, *CHROME_FLAGS, f'--user-data-dir={td}/profile', '--dump-dom', probe.as_uri()],
                         capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
    m = re.search(r'<pre id="cover-check"[^>]*>(.*?)</pre>', res.stdout, re.S)
    if not m or not m.group(1).strip():
        return ['Chrome 量測沒有回傳結果（字型與版位驗證未完成），不產圖']
    r = json.loads(html.unescape(m.group(1)))
    errs = []
    if r.get('error'):
        errs.append(f'量測腳本錯誤：{r["error"]}')
    for alias in fonts:
        if not r.get('loads', {}).get(alias):
            errs.append(f'{alias} 字型沒有被 Chrome 載入')
    bad = [f for f in r.get('faces', []) if f.get('status') != 'loaded']
    if bad:
        errs.append(f'字型載入失敗 {bad}')
    boxes = r.get('boxes', {})
    if len(boxes) != 4:
        errs.append(f'版位量測不完整 {sorted(boxes)}')
    for sel, b in boxes.items():
        top, bottom = Y_LIMITS.get(sel, (TEXT_TOP, TEXT_BOTTOM))
        if (b['left'] < SAFE_LEFT - TOL or b['right'] > SAFE_RIGHT + TOL
                or b['top'] < top - TOL or b['bottom'] > bottom + TOL):
            errs.append(f'{sel} 越界：x {b["left"]:.1f}–{b["right"]:.1f}、y {b["top"]:.1f}–{b["bottom"]:.1f}'
                        f'（限 x {SAFE_LEFT}–{SAFE_RIGHT}、y {top}–{bottom}）')
    show, heads = boxes.get('.show'), [boxes[s] for s in ('.headline', '.hl') if s in boxes]
    if show and heads and show['top'] < max(h['bottom'] for h in heads) - TOL:
        errs.append('節目名黃框與主標重疊；節目名必須在主標正下方')
    return errs


def render(item, out_dir, exe):
    out = out_dir / f'{item["day"]}-cover.png'
    with tempfile.TemporaryDirectory() as td:
        tpl = build_page(item, td)
        page = Path(td) / 'cover.html'
        probe = Path(td) / 'probe.html'
        page.write_text(tpl, encoding='utf-8')
        probe.write_text(tpl.replace('</body>', PROBE + '</body>'), encoding='utf-8')
        errs = verify(probe, exe, td, item['fonts'])
        if errs:
            return None, errs
        subprocess.run([exe, *CHROME_FLAGS, f'--user-data-dir={td}/profile', f'--screenshot={out}', page.as_uri()],
                       check=True, capture_output=True)
    thumb = out_dir / f'{item["day"]}-cover-grid-check.png'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(out), '-vf', 'crop=1080:1440:0:240,scale=264:-1', str(thumb)],
                   check=True)
    sheet = out_dir / f'{item["day"]}-cover-vs-shots.png'
    ins = [item['art_path']] + item['shot_paths']
    args = ['ffmpeg', '-v', 'error', '-y']
    for p in ins:
        args += ['-i', p]
    fc = ''.join(f'[{i}]scale=300:534:force_original_aspect_ratio=decrease,pad=300:534:(ow-iw)/2:(oh-ih)/2:white'
                 f'{",drawbox=0:0:300:534:yellow:8" if i == 0 else ""}[v{i}];' for i in range(5))
    fc += ''.join(f'[v{i}]' for i in range(5)) + 'hstack=5'
    subprocess.run(args + ['-filter_complex', fc, str(sheet)], check=True)
    return (out, thumb, sheet), []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('out_dir')
    ap.add_argument('--shots', action='append', default=[])
    a = ap.parse_args()
    spec = Path(a.spec)
    items = json.loads(spec.read_text(encoding='utf-8'))
    shot_hashes = {sha(p) for d in a.shots for p in Path(d).rglob('*') if p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp')}
    out_dir = Path(a.out_dir)
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
        if errs:
            bad = True
            print(f'FAIL {it.get("day")}：' + '；'.join(errs))
            continue
        files, errs = render(it, out_dir, chrome())
        if errs:
            bad = True
            print(f'FAIL {it.get("day")}：' + '；'.join(errs))
            continue
        out, thumb, sheet = files
        used = '、'.join(f'{k}={p.name}（{w}）' for k, (p, w) in it['fonts'].items())
        print(f'OK   {it["day"]}：{out}（字型 {used}；格狀牆縮圖 {thumb.name}；'
              f'對照圖 {sheet.name} 交鐵雄確認不是影片圖的裁切或重繪）')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
