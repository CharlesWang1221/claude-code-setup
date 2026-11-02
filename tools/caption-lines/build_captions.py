#!/usr/bin/env python3
"""句剪逐字字幕：TXT 一行＝一框，按 Whisper 逐字時間碼出現。

用法：
  python3 tools/caption-lines/build_captions.py <字幕校對.txt> <whisper_json_dir> <compositions_dir> \
      [--overrides overrides.json] [--report caption-timing.json]

- <whisper_json_dir>/<day>.json：whisper --word_timestamps True --output_format json 的結果，
  day 為 mon tue wed thu fri sat，對應 <compositions_dir>/<day>-quote.html。
- overrides.json：{"sat": {"給三明治的我們": 16.64}}，只用在整段 Whisper 漏聽、
  已用切段重聽取得時間的行；每筆都會列入報告。
- 字幕框樣式固定為 S4EP2 週二 v8（老查核准），不得在此改設計。
- 禁止按字數平均分配時間。對不到的行會列旗標，交件前必須逐條處理。
"""
import argparse
import difflib
import html
import json
import re
from pathlib import Path

DAYS = {'週一': 'mon', '週二': 'tue', '週三': 'wed', '週四': 'thu', '週五': 'fri', '週六': 'sat'}
CUE = re.compile(r'^\s*\d+\.\s*(\d\d):(\d\d):(\d\d)[,.](\d{3})\s*-->\s*(\d\d):(\d\d):(\d\d)[,.](\d{3})')
KEEP = re.compile(r'[㐀-鿿A-Za-z0-9]')
MIN_DWELL = 0.30   # 兩行之間最短間隔，避免同格閃現
LEAD = 0.18        # 前幾字對不到時，每字往前推估的秒數
CSS = ('<style>@font-face{font-family:NotoTC;src:url("../assets/NotoSansTC-VF.ttf")}'
       '.caption{position:absolute;left:76px;bottom:410px;width:928px;padding:12px 18px 14px;color:#fff;'
       'background:rgba(36,35,31,.82);border-radius:13px;font:700 94px/1.2 NotoTC,sans-serif;letter-spacing:0;'
       'text-align:center;text-wrap:pretty;overflow-wrap:anywhere;z-index:99;'
       'text-shadow:0 1px 2px rgba(0,0,0,.65);opacity:0}.caption.emph{background:#D96535}</style>')
TL = 'const tl=gsap.timeline({paused:true});'


def secs(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def parse_txt(path):
    days, day, cue = {}, None, None
    for raw in Path(path).read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if m := re.match(r'^【(.+?)】', line):
            day = DAYS.get(m.group(1))
            if day:
                days[day] = []
            cue = None
        elif m := CUE.match(line):
            g = m.groups()
            cue = (secs(*g[:4]), secs(*g[4:]))
        elif line and day and cue:
            days[day].append({'text': line.lstrip('★').strip(), 'emph': line.startswith('★'), 'cue': cue})
    return days


def char_times(path):
    out = []
    for seg in json.loads(Path(path).read_text())['segments']:
        for w in seg.get('words', []):
            chars = KEEP.findall(w['word'])
            step = (w['end'] - w['start']) / max(len(chars), 1)
            out += [(c, w['start'] + i * step, w['start'] + (i + 1) * step) for i, c in enumerate(chars)]
    return out


def align(lines, ctimes, duration, overrides):
    tchars = [c for ln in lines for c in KEEP.findall(ln['text'])]
    sm = difflib.SequenceMatcher(None, tchars, [c for c, _, _ in ctimes], autojunk=False)
    match = {a + k: b + k for a, b, n in sm.get_matching_blocks() for k in range(n)}
    flags, pos = [], 0
    for ln in lines:
        n = len(KEEP.findall(ln['text']))
        hit = [(k, match[pos + k]) for k in range(n) if pos + k in match]
        pos += n
        cs, ce = ln['cue']
        if ln['text'] in overrides:
            ln['start'] = ln['last_end'] = overrides[ln['text']]
            flags.append(f'{ln["text"]}：用切段重聽時間 {ln["start"]:.2f}')
        elif not hit:
            ln['start'] = cs
            flags.append(f'{ln["text"]}：原音對不到任何字，需切段重聽後寫入 overrides')
        else:
            k, b = hit[0]
            ln['start'] = ctimes[b][1] - k * LEAD
            ln['last_end'] = ctimes[hit[-1][1]][2]
            if k > 1:
                flags.append(f'{ln["text"]}：前 {k} 字對不到，起點由第 {k + 1} 字推估，需抽聽')
            if not (cs - 0.6 <= ln['start'] <= ce + 0.3):
                flags.append(f'{ln["text"]}：開口 {ln["start"]:.2f} 秒落在時段 {cs:.2f}–{ce:.2f} 外，需切段重聽')
    lines[0]['start'] = 0.0  # 第 0 格就要看得到鉤子字幕
    for a, b in zip(lines, lines[1:]):
        b['start'] = max(b['start'], a['start'] + MIN_DWELL)
    for i, ln in enumerate(lines):
        nxt = lines[i + 1]['start'] if i + 1 < len(lines) else duration - 0.1
        ln['end'] = round(min(nxt, max(ln['cue'][1], ln.get('last_end', 0) + 0.3)), 3)
        ln['start'] = round(ln['start'], 3)
    for a, b in zip(lines, lines[1:]):
        assert a['end'] <= b['start'] + 1e-6, f'字幕重疊：{a["text"]} / {b["text"]}'
    return flags


def patch(path, lines):
    s = path.read_text()
    divs = ''.join(f'<div id="caption-{i}" class="caption{" emph" if ln["emph"] else ""}">'
                   f'{html.escape(ln["text"])}</div>' for i, ln in enumerate(lines, 1))
    if '.caption{' not in s:
        s = s.replace('</head>', CSS + '</head>', 1)
    s, n = re.subn(r'(<div id="caption-\d+" class="caption[^"]*">[^<]*</div>)+', divs, s, count=1)
    if not n:  # 新專案：放在 root 結尾、timeline script 之前
        i = s.rfind('</div><script')
        assert i >= 0, f'{path.name}：找不到插入點'
        s = s[:i] + divs + s[i:]
    s = re.sub(r'tl\.set\("#caption-\d+",\{autoAlpha:[01]\},[\d.]+\);', '', s)
    assert s.count(TL) == 1, f'{path.name}：timeline 宣告必須是 {TL}'
    sets = ''.join(f'tl.set("#caption-{i}",{{autoAlpha:1}},{ln["start"]:.3f});'
                   f'tl.set("#caption-{i}",{{autoAlpha:0}},{ln["end"]:.3f});' for i, ln in enumerate(lines, 1))
    path.write_text(s.replace(TL, TL + sets))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('txt')
    ap.add_argument('whisper_dir')
    ap.add_argument('comp_dir')
    ap.add_argument('--overrides')
    ap.add_argument('--report', default='caption-timing.json')
    a = ap.parse_args()
    ov = json.loads(Path(a.overrides).read_text()) if a.overrides else {}
    report = {}
    for day, lines in parse_txt(a.txt).items():
        comp = Path(a.comp_dir) / f'{day}-quote.html'
        dur = float(re.search(r'data-duration="([\d.]+)"', comp.read_text()).group(1))
        flags = align(lines, char_times(Path(a.whisper_dir) / f'{day}.json'), dur, ov.get(day, {}))
        patch(comp, lines)
        report[day] = {'flags': flags, 'lines': [{k: ln[k] for k in ('text', 'emph', 'start', 'end')} for ln in lines]}
        print(f'{day}: {len(lines)} 行，旗標 {len(flags)}')
        for f in flags:
            print('  ⚠', f)
    Path(a.report).write_text(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
