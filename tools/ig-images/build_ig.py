#!/usr/bin/env python3
"""
IG 圖片 HTML 產生器（金句圖 × 3 + 輪播 × 5）
用法: python build_ig.py <show_notes.md> <cover_image> <output_dir>
"""
import base64, os, sys, re, html as _html

if len(sys.argv) < 4:
    print("Usage: python build_ig.py <show_notes.md> <cover_image|--auto> <output_dir>", file=sys.stderr)
    sys.exit(1)

NOTES    = sys.argv[1]
COVER    = sys.argv[2]
OUT_DIR  = sys.argv[3]

# Auto-detect cover image from Google Drive
if COVER == '--auto':
    GDRIVE = r"G:\我的雲端硬碟\不標準答案\2026\網誌\節目"
    # Derive episode slug from show-notes path or NOTES filename
    # e.g. output/ep-s2ep7/show-notes.md -> s2ep7
    slug_m = re.search(r'ep-([^/\\]+)[/\\]', NOTES)
    slug = slug_m.group(1) if slug_m else ''
    COVER = ''
    if slug and os.path.isdir(GDRIVE):
        for d in os.listdir(GDRIVE):
            if d.lower() == slug.lower() or d.lower().replace('-','') == slug.lower():
                folder = os.path.join(GDRIVE, d)
                pngs = [f for f in os.listdir(folder)
                        if f.lower().endswith('.png') and f[0].isascii() and f[0].isalnum()]
                # prefer _V2
                v2 = [f for f in pngs if '_v2' in f.lower()]
                pick = v2[0] if v2 else (pngs[0] if pngs else None)
                if pick:
                    COVER = os.path.join(folder, pick)
                    print(f"Cover (auto): {COVER}")
                break
    if not COVER or not os.path.exists(COVER):
        print("ERROR: Could not auto-detect cover image. Use explicit path.", file=sys.stderr)
        sys.exit(1)
HTML_DIR = os.path.join(OUT_DIR, 'html')
os.makedirs(HTML_DIR, exist_ok=True)

# ── 讀 show-notes.md ───────────────────────────────────────────────────────────
with open(NOTES, encoding='utf-8') as f:
    md = f.read()

# 標題
m = re.search(r'^# (.+)$', md, re.MULTILINE)
full_title = m.group(1).strip() if m else '不標準答案'

# 集數（S2EP7 → S2E07）
ep_m = re.search(r'(S\d+EP?\d+)', full_title, re.IGNORECASE)
if ep_m:
    raw = ep_m.group(1).upper()
    ep_num = re.sub(r'EP?(\d)$',    lambda x: f'E0{x.group(1)}', raw)
    ep_num = re.sub(r'EP?(\d{2,})$', lambda x: f'E{x.group(1)}',  ep_num)
else:
    ep_num = ''

# 顯示用標題（去掉 "S2EP7 — " 前綴）
title_clean = re.sub(r'^S\d+EP?\d+\s*[—–\-]+\s*', '', full_title, flags=re.IGNORECASE).strip()

# 時長
dur_m = re.search(r'\*\*時長[：:]\*\*\s*(.+)', md)
duration = dur_m.group(1).strip() if dur_m else ''

# ── 金句（從 ## 金句 區塊抓 > 「...」—— speaker ）─────────────────────────────
quotes = []
qs_sec = re.search(r'## 金句\s*\n([\s\S]+?)(?=\n## |\Z)', md)
if qs_sec:
    for m in re.finditer(r'^>\s*「([^」]{10,})」\s*——\s*(.+)$', qs_sec.group(1), re.MULTILINE):
        quotes.append({'text': m.group(1).strip(), 'speaker': m.group(2).strip()})

# fallback：掃全文 blockquote
if not quotes:
    for m in re.finditer(r'^>\s*「([^」]{10,})」', md, re.MULTILINE):
        quotes.append({'text': m.group(1).strip(), 'speaker': '老查 × 阿分'})

quotes = quotes[:3]
while len(quotes) < 3:
    quotes.append(quotes[0] if quotes else {'text': title_clean, 'speaker': '老查 × 阿分'})

# ── 重點（## 核心討論 下的 H3 標題）─────────────────────────────────────────────
key_points = []
core_sec = re.search(r'##\s+核心討論\s*\n([\s\S]+?)(?=\n## |\Z)', md)
src = core_sec.group(1) if core_sec else md
for m in re.finditer(r'^### (.+)$', src, re.MULTILINE):
    key_points.append(m.group(1).strip())
    if len(key_points) >= 3:
        break

while len(key_points) < 3:
    key_points.append('本集重點')

# ── 封面圖 base64 ─────────────────────────────────────────────────────────────
with open(COVER, 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()
ext  = os.path.splitext(COVER)[1].lower().lstrip('.')
mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else f'image/{ext}'
IMG  = f"data:{mime};base64,{img_b64}"

# ── 工具 ──────────────────────────────────────────────────────────────────────
def e(t): return _html.escape(str(t))

def quote_font_size(text):
    l = len(text)
    if l > 70: return '34px'
    if l > 45: return '42px'
    return '52px'

NAVY      = '#112D4E'
NAVY_DARK = '#0C1F35'
TEAL      = '#3F72AF'
CORAL     = '#E07A5F'

# ── 金句圖 ────────────────────────────────────────────────────────────────────
def quote_html(q):
    fs = quote_font_size(q['text'])
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;overflow:hidden;background:{NAVY};
     font-family:'Microsoft JhengHei','微軟正黑體',sans-serif}}
.bg{{position:absolute;inset:0;background:url('{IMG}') center/cover no-repeat}}
.ov{{position:absolute;inset:0;background:rgba(12,31,53,0.83)}}
.wrap{{position:relative;width:1080px;height:1080px;display:flex;
       flex-direction:column;padding:72px 80px}}
.show{{color:{CORAL};font-size:24px;letter-spacing:8px;font-weight:400}}
.mid{{flex:1;display:flex;align-items:center;gap:32px;padding:20px 0}}
.bar{{width:5px;min-height:180px;background:{CORAL};border-radius:4px;flex-shrink:0;align-self:stretch}}
.qt{{color:#fff;font-size:{fs};line-height:1.8;font-weight:500}}
.foot{{display:flex;justify-content:space-between;align-items:flex-end}}
.spk{{color:rgba(255,255,255,0.55);font-size:22px}}
.hdl{{color:{TEAL};font-size:22px}}
</style></head><body>
<div class="bg"></div><div class="ov"></div>
<div class="wrap">
  <div class="show">不 標 準 答 案</div>
  <div class="mid">
    <div class="bar"></div>
    <div class="qt">「{e(q['text'])}」</div>
  </div>
  <div class="foot">
    <div class="spk">{e(q['speaker'])} ｜ {e(ep_num)}</div>
    <div class="hdl">@beyond_ans</div>
  </div>
</div>
</body></html>"""

# ── 輪播：封面 ────────────────────────────────────────────────────────────────
def carousel_cover():
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;overflow:hidden;
     font-family:'Microsoft JhengHei','微軟正黑體',sans-serif}}
.bg{{position:absolute;inset:0;background:url('{IMG}') center/cover no-repeat}}
.ov{{position:absolute;inset:0;
     background:linear-gradient(to bottom,rgba(12,31,53,0.55) 0%,rgba(12,31,53,0.94) 100%)}}
.wrap{{position:relative;width:1080px;height:1080px;display:flex;
       flex-direction:column;padding:72px 80px}}
.tag{{display:inline-block;background:{CORAL};color:#fff;font-size:22px;
      padding:8px 22px;border-radius:4px;margin-bottom:20px;width:fit-content}}
.ep{{color:{TEAL};font-size:28px;margin-bottom:16px}}
.title{{flex:1;display:flex;align-items:center;color:#fff;
        font-size:52px;font-weight:700;line-height:1.5}}
.foot{{display:flex;justify-content:space-between;align-items:flex-end}}
.dur{{color:rgba(255,255,255,0.45);font-size:22px}}
.swipe{{color:{TEAL};font-size:22px}}
</style></head><body>
<div class="bg"></div><div class="ov"></div>
<div class="wrap">
  <div class="tag">本集聊了什麼</div>
  <div class="ep">{e(ep_num)}</div>
  <div class="title">{e(title_clean)}</div>
  <div class="foot">
    <div class="dur">{e(duration)}</div>
    <div class="swipe">往下滑看精華 →</div>
  </div>
</div>
</body></html>"""

# ── 輪播：重點 ────────────────────────────────────────────────────────────────
def carousel_point(idx, point, slide_n, total):
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;overflow:hidden;background:{NAVY_DARK};
     font-family:'Microsoft JhengHei','微軟正黑體',sans-serif}}
.wrap{{width:1080px;height:1080px;display:flex;flex-direction:column;padding:80px}}
.num{{color:{CORAL};font-size:110px;font-weight:700;line-height:1;opacity:0.9}}
.pt{{flex:1;display:flex;align-items:center;color:#fff;
     font-size:56px;font-weight:700;line-height:1.55}}
.div{{width:56px;height:4px;background:{TEAL};border-radius:2px;margin:28px 0}}
.foot{{display:flex;justify-content:space-between;align-items:center}}
.show{{color:rgba(255,255,255,0.3);font-size:20px;letter-spacing:5px}}
.pg{{color:rgba(255,255,255,0.25);font-size:20px}}
</style></head><body>
<div class="wrap">
  <div class="num">{idx:02d}</div>
  <div class="pt">{e(point)}</div>
  <div class="div"></div>
  <div class="foot">
    <div class="show">不 標 準 答 案</div>
    <div class="pg">{slide_n} / {total}</div>
  </div>
</div>
</body></html>"""

# ── 輪播：CTA ─────────────────────────────────────────────────────────────────
def carousel_cta():
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1080px;overflow:hidden;
     font-family:'Microsoft JhengHei','微軟正黑體',sans-serif}}
.wrap{{width:1080px;height:1080px;
       background:linear-gradient(135deg,{NAVY} 0%,{TEAL} 100%);
       display:flex;flex-direction:column;align-items:center;
       justify-content:center;padding:80px;text-align:center}}
.sub{{color:rgba(255,255,255,0.6);font-size:28px;letter-spacing:4px;margin-bottom:20px}}
.main{{color:#fff;font-size:66px;font-weight:700;line-height:1.4;margin-bottom:16px}}
.desc{{color:rgba(255,255,255,0.5);font-size:26px;margin-bottom:56px}}
.btn{{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);
      color:#fff;font-size:28px;padding:20px 48px;border-radius:40px;margin-bottom:44px}}
.info{{color:rgba(255,255,255,0.38);font-size:22px}}
</style></head><body>
<div class="wrap">
  <div class="sub">完 整 集 數</div>
  <div class="main">在 Firstory<br>等你</div>
  <div class="desc">Show Notes 連結在 bio</div>
  <div class="btn">🎙 Firstory · Spotify · Apple</div>
  <div class="info">《不標準答案》{e(ep_num)}</div>
</div>
</body></html>"""

# ── 寫出 HTML 檔案 ────────────────────────────────────────────────────────────
TOTAL = 5

print("=== 金句圖 ===")
for i, q in enumerate(quotes, 1):
    path = os.path.join(HTML_DIR, f'quote_{i}.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(quote_html(q))
    preview = q['text'][:35] + ('...' if len(q['text']) > 35 else '')
    print(f"  [{i}] 「{preview}」 —— {q['speaker']}")

print("\n=== 輪播 ===")
slides = [
    carousel_cover(),
    carousel_point(1, key_points[0], 2, TOTAL),
    carousel_point(2, key_points[1], 3, TOTAL),
    carousel_point(3, key_points[2], 4, TOTAL),
    carousel_cta(),
]
labels = ['封面', key_points[0][:20], key_points[1][:20], key_points[2][:20], 'CTA']
for i, (html, label) in enumerate(zip(slides, labels), 1):
    path = os.path.join(HTML_DIR, f'carousel_{i}.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  [{i}] {label}")

print(f"\nDone: {3 + TOTAL} HTML -> {HTML_DIR}")
