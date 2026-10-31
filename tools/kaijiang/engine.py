"""嘴型元件（開講試點 v12）：words.json + 音檔 + 角色前視圖 → 大／小兩種尺寸 MP4。"""
import sys, os, json, math, random, subprocess, re, wave
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pypinyin import pinyin, Style
sys.path.insert(0, sys.argv[1]); import mouths as M  # noqa
SRC, WORDS, WAV, AUDIO, FONT, OUT = sys.argv[2:8]
FPS = 30; random.seed(7)

# ---- 6 種嘴型的頭像底圖（含眨眼版本）
base = Image.open(SRC).convert('RGB')
CROP = (110, 180, 870, 1180)
shapes = dict(M.shapes)
mouth_dir = os.environ.get('MOUTHS', '')
ink_mouths = {}
if mouth_dir:
    for name in shapes:
        path = os.path.join(mouth_dir, name + '.png')
        try:
            with Image.open(path) as src:
                if src.mode != 'RGBA' or src.size not in (base.size, (260, 140)):
                    raise ValueError('需要 RGBA 透明 PNG，尺寸為原圖或 260 × 140')
                layer = src.copy()
            alpha = layer.getchannel('A')
            box = alpha.point(lambda a: 255 if a >= 20 else 0).getbbox()
            if box is None:
                raise ValueError('嘴型沒有可見像素')
            ox, oy = (0, 0) if layer.size == base.size else (M.CX-130, M.CY-70)
            x0, y0, x1, y1 = box
            if not (M.CX-100 <= ox+x0 and ox+x1 <= M.CX+100 and 578 <= oy+y0 and oy+y1 <= 655):
                raise ValueError('嘴型超出既有擦除框')
            ink_mouths[name] = layer
        except (OSError, ValueError) as exc:
            print(f'嘴型 {name} 無法讀取（{exc}），退回程式嘴型', flush=True)
def with_mouth(name):
    f = base.copy()
    if name in ink_mouths:
        f = M.erase(f, 50).convert('RGBA')
        layer = ink_mouths[name]
        f.alpha_composite(layer, (0, 0) if layer.size == base.size else (M.CX-130, M.CY-70))
        return f.convert('RGB')
    if shapes[name]:
        f = M.erase(f, 50); L, o = M.render(shapes[name]); f.paste(L, o, L)
    return f
EYES = [(400, 484), (562, 484)]
A = np.asarray(base).astype(float)
def lens_color(x, y):
    p = A[y-45:y+45, x-45:x+45].reshape(-1, 3); p = p[p.mean(1) > 170]
    return tuple(int(v) for v in np.median(p, axis=0))
def blink(img):
    f = img.copy(); d = ImageDraw.Draw(f)
    for x, y in EYES:
        d.ellipse((x-30, y-38, x+24, y+28), fill=lens_color(x, y))
        d.arc((x-17, y-12, x+17, y+10), 20, 160, fill=M.INK, width=8)
    return f
frames = {}
for n in shapes:
    m = with_mouth(n)
    frames[(n, 0)] = m; frames[(n, 1)] = blink(m)
def feather(size, e=40):
    w, h = size; a = np.ones((h, w))
    r = np.minimum(np.arange(w) / e, 1); a *= np.minimum(r, r[::-1])[None, :]
    c = np.minimum(np.arange(h) / e, 1); a *= c[:, None]
    return Image.fromarray((a * 255).astype(np.uint8))
CROPS = {'big': (90, 180, 910, 1310), 'small': (110, 190, 870, 1310)}  # small＝腰上鏡位
# 去背：從畫面四角往內 flood fill 亮色紙底，剩下的就是人物；已有透明度的圖直接用
def cutout(img):
    if img.mode == 'RGBA' and np.asarray(img.getchannel('A')).min() < 250: return img.getchannel('A')
    g = img.convert('L').point(lambda v: 255 if v > 205 else 0)
    for seed in [(5, 5), (img.width-6, 5), (5, img.height-6), (img.width-6, img.height-6), (img.width//2, 5)]:
        ImageDraw.floodfill(g, seed, 128)
    return Image.fromarray(np.where(np.asarray(g) == 128, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
CUT = cutout(base)
# ---- 頭身分層：沿前視頭部外輪廓切，排除原圖衣領與肩線。
# 下巴弧線只保留臉部像素，姿勢圖獨自提供頸部、衣領和肩膀。
HEAD_CONTOUR = [
    (160, 0), (850, 0), (850, 450), (780, 450), (780, 510),
    (760, 550), (730, 585), (705, 620), (670, 650), (625, 675),
    (580, 692), (540, 701), (490, 706), (440, 701), (400, 692),
    (355, 675), (315, 650), (280, 620), (250, 585), (225, 550),
    (205, 510), (205, 450), (160, 450),
]
HEAD = Image.new('L', base.size, 0)
ImageDraw.Draw(HEAD).polygon(HEAD_CONTOUR, fill=255)
HEAD_A = Image.fromarray(np.minimum(np.asarray(CUT), np.asarray(HEAD.filter(ImageFilter.GaussianBlur(2)))))
POSE_NAMES = ['垂手', '攤手', '手指', '托腮', '胸口', '搔頭']
POSES, FRONT, MISSING = {}, {}, []
_pd = os.environ.get('POSES', '')
for n in POSE_NAMES:
    fp = os.path.join(_pd, n + '.png')
    src = Image.open(fp) if _pd and os.path.exists(fp) else base
    if src is base and n != '垂手': MISSING.append(n)
    body = src.convert('RGBA'); body.putalpha(cutout(src)); POSES[n] = body
    fr = os.path.join(_pd, n + '_前.png')
    if _pd and os.path.exists(fr): FRONT[n] = Image.open(fr).convert('RGBA')
if MISSING: print('缺姿勢圖，暫用垂手：', MISSING)

# ---- 字 → 嘴型
def viseme(ch):
    if not re.match(r'[一-鿿]', ch): return None
    p = pinyin(ch, style=Style.NORMAL, strict=False)[0][0]
    ini = pinyin(ch, style=Style.INITIALS, strict=False)[0][0]
    fin = p[len(ini):] if p.startswith(ini) else p
    lip = ini in ('b', 'p', 'm')
    if fin in ('ou', 'iu'): seq = ('小開', '圓')
    elif fin == 'ui': seq = ('圓', '扁')
    elif fin == 'uo': seq = ('圓', '小開')
    elif ini in ('zh', 'ch', 'sh', 'r', 'z', 'c', 's') and fin == 'i': seq = ('扁',)
    elif fin.endswith(('a', 'an', 'ang', 'ao')): seq = ('大開',)
    elif fin in ('u', 'v', 'ü', 'o', 'ong'): seq = ('小開', '圓', '圓')  # 起口過渡後才收圓
    elif fin.startswith('i') or fin in ('ai', 'ei', 'in', 'ing'): seq = ('扁',)
    else: seq = ('小開',)
    return lip, seq
words = json.load(open(WORDS, encoding='utf-8'))  # Windows 預設 cp950，要明指
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', WAV]))
N = int(dur * FPS)
track = ['閉'] * N
for w in words:
    chars = [c for c in w['w'] if viseme(c)]
    if not chars: continue
    span = max(w['e'] - w['s'], 0.08) / len(chars)
    for k, c in enumerate(chars):
        lip, seq = viseme(c); s = w['s'] + k * span; e = s + span
        for f in range(int(s * FPS), min(N, int(e * FPS) + 1)):
            t = (f / FPS - s) / span
            track[f] = '抿' if lip and t < 0.3 else seq[min(int(t * len(seq)), len(seq)-1)]

def runs(values):
    starts = [0] + [i for i in range(1, len(values)) if values[i] != values[i-1]] + [len(values)]
    return [(a, b, values[a]) for a, b in zip(starts, starts[1:])]

# 最短 2 格：過短口形併入相鄰較長的一段，避免 30 fps 下單格閃爍。
while True:
    rr = runs(track)
    short_idx = next((i for i, (a, b, _) in enumerate(rr) if b-a < 2), None)
    if short_idx is None: break
    a, b, _ = rr[short_idx]
    left_len = rr[short_idx-1][1] - rr[short_idx-1][0] if short_idx else -1
    right_len = rr[short_idx+1][1] - rr[short_idx+1][0] if short_idx+1 < len(rr) else -1
    replacement = rr[short_idx-1][2] if left_len >= right_len else rr[short_idx+1][2]
    track[a:b] = [replacement] * (b-a)

# 大開 ↔ 閉必經小開 2 格；長度不足時捨棄該次大開，保留閉嘴休止。
while True:
    rr = runs(track)
    boundary = next(((left, right) for left, right in zip(rr, rr[1:]) if {left[2], right[2]} == {'大開', '閉'}), None)
    if boundary is None: break
    (a, b, v), (c, d, w) = boundary
    if v == '大開' and b-a >= 4: track[b-2:b] = ['小開'] * 2
    elif w == '大開' and d-c >= 4: track[c:c+2] = ['小開'] * 2
    elif v == '閉' and b-a >= 4: track[b-2:b] = ['小開'] * 2
    elif w == '閉' and d-c >= 4: track[c:c+2] = ['小開'] * 2
    else:
        s, e = (a, b) if v == '大開' else (c, d)
        track[s:e] = ['小開'] * (e-s)

rr = runs(track)
if any(b-a < 2 for a, b, _ in rr): raise RuntimeError('存在少於 2 格的嘴型')
if any({x[2], y[2]} == {'大開', '閉'} for x, y in zip(rr, rr[1:])): raise RuntimeError('大開與閉缺小開過渡')
counts = Counter(track)
shares = {name: round(counts[name] / N, 4) for name in shapes}
print('mouth shares', shares, 'min hold', min(b-a for a, b, _ in rr), flush=True)
if shares['圓'] >= 0.20: raise RuntimeError('圓嘴型佔比達 20%，須調整韻母規則')
with open(OUT + '-viseme-stats.json', 'w', encoding='utf-8') as fh:
    json.dump({'fps': FPS, 'frames': N, 'counts': dict(counts), 'shares': shares,
               'min_hold_frames': min(b-a for a, b, _ in rr)}, fh, ensure_ascii=False, indent=2)
if os.environ.get('MOUTH_SHEET_START') is not None:
    start = int(float(os.environ['MOUTH_SHEET_START']) * FPS)
    if start < 0 or start + 4*FPS > N: raise ValueError('嘴部聯絡表須為完整連續 4 秒')
    font_sheet = ImageFont.truetype(FONT, 21)
    sheet = Image.new('RGB', (12*260, 10*155), 'white')
    for k in range(4*FPS):
        f = start + k
        tile = frames[(track[f], 0)].crop((360, 545, 620, 675))
        sheet.paste(tile, ((k%12)*260, (k//12)*155+25))
        ImageDraw.Draw(sheet).text(((k%12)*260+4, (k//12)*155+2),
                                   f'{f/FPS:.2f}s {track[f]}', fill=(25, 25, 25), font=font_sheet)
    sheet.save(OUT + '-mouth-4s.png')

# ---- 音量包絡 → 重音點頭
with wave.open(WAV) as wv:
    sr = wv.getframerate(); a = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).astype(float)
hop = sr // FPS
rms = np.array([np.sqrt(np.mean(a[i*hop:(i+1)*hop]**2)) if i*hop < len(a) else 0 for i in range(N)])
rms = np.convolve(rms, np.ones(5)/5, 'same'); thr = np.percentile(rms, 88)
nods = []
for i in range(2, N-2):
    if rms[i] > thr and rms[i] == rms[i-2:i+3].max() and (not nods or i - nods[-1] > FPS * 0.7): nods.append(i)
# ---- 問句歪頭（疑問詞或問號）
tilts = [w['s'] for w in words if re.search(r'[嗎呢？?]|怎麼|什麼|為什麼', w['w'])]
blinks = []; t = 1.0
while t < dur: blinks.append(int(t * FPS)); t += random.uniform(2.5, 5)

# ---- 姿勢排程：比方說／例如→攤手；序數與數量→手指；疑問→托腮；講自己→胸口；語塞／轉折→搔頭；其餘垂手
# 同一姿勢至少 HOLD 秒、任 10 秒內最多切 2 次（回到垂手也算一次），切換交叉淡化 XF 秒
HOLD, XF = 3.0, 0.15
NUM = r'第[一二三四五六七八九十]|[0-9０-９]|[兩二三四五六七八九十百千萬]+(個|次|年|天|點|種|件|塊|歲|成|%)'
cues = []
for i, w in enumerate(words):
    ctx = w['w'] + ''.join(x['w'] for x in words[i+1:i+3])  # 「比／方／說」常被拆成單字
    if re.match(r'比方|例如|舉例|譬如', ctx): cues.append((w['s'], '攤手'))
    elif re.search(NUM, w['w']): cues.append((w['s'], '手指'))
    elif re.search(r'[嗎呢？?]|為什麼', w['w']): cues.append((w['s'], '托腮'))  # 「會怎麼想我」不是問句，怎麼／什麼不算
    elif re.match(r'我覺得|我是|我自己|對我來說', ctx): cues.append((w['s'], '胸口'))
    elif re.match(r'其實|不好意思|啊[,，]?$', w['w']): cues.append((w['s'], '搔頭'))
switches = [(0.0, '垂手')]
def can_switch(t):
    return t - switches[-1][0] >= HOLD and sum(1 for s, _ in switches[1:] if t - 10 < s <= t) < 2
back = None  # 手勢做完 HOLD 秒收回垂手；被頻率擋住就順延
for t, p in cues + [(dur, None)]:
    if back is not None and back < t:
        while back < t and not can_switch(back): back += 0.5
        if back < t: switches.append((back, '垂手')); back = None
    if p and p == switches[-1][1]: back = t + HOLD
    elif p and can_switch(t): switches.append((t, p)); back = t + HOLD
def body_at(tt):
    k = max(i for i, (s, _) in enumerate(switches) if s <= tt)
    cur = switches[k][1]; prev = switches[k-1][1] if k else cur
    return prev, cur, min((tt - switches[k][0]) / XF, 1) if k else 1

def pose(f):
    dy = sum(9 * math.exp(-((f - n) / 4) ** 2) for n in nods)
    ang = sum(3.5 * math.exp(-((f / FPS - s - 0.4) / 0.45) ** 2) for s in tilts)
    breathe = 1 + 0.006 * math.sin(f / FPS * 2 * math.pi / 3.6)
    return dy, ang, breathe

# ---- 字幕片段
segs = []; cur = ''; st = None
for w in words:
    if st is None: st = w['s']
    cur += w['w']
    if re.search(r'[，。,.!?！？]$', w['w']) or len(cur) > 14:
        segs.append((st, w['e'], cur.strip('，。,. '))); cur = ''; st = None
if cur: segs.append((st, words[-1]['e'], cur))
font_big = ImageFont.truetype(FONT, 64); font_small = ImageFont.truetype(FONT, 46)
PAPER = tuple(int(v) for v in np.median(np.asarray(base)[30:120, 30:120].reshape(-1, 3), axis=0))

def avatar(f, scale, kind):
    mouth = track[f]; b = 1 if any(0 <= f - x < 4 for x in blinks) else 0
    prev, cur, mix = body_at(f / FPS)
    body = POSES[cur] if mix >= 1 else Image.blend(POSES[prev], POSES[cur], mix)
    body = body.copy(); head = frames[(mouth, b)].convert('RGBA'); head.putalpha(HEAD_A); body.alpha_composite(head)
    for name, opacity in ((prev, 1-mix), (cur, mix)) if mix < 1 else ((cur, 1),):
        if name in FRONT and opacity > 0:
            hand = FRONT[name].copy()
            hand.putalpha(hand.getchannel('A').point(lambda a: round(a * opacity)))
            body.alpha_composite(hand)
    im = body.crop(CROPS[kind]); dy, ang, br = pose(f)
    w, h = im.size; s = scale * br
    im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    fade = np.asarray(im.getchannel('A')).astype(float) * np.minimum(np.arange(im.height)[::-1] / 30, 1)[:, None]
    im.putalpha(Image.fromarray(fade.astype(np.uint8)))  # 只淡出底部裁切邊
    im = im.rotate(ang, resample=Image.BICUBIC, center=(w*s/2, h*s))
    return im, dy * scale

def render(kind, out):
    W, H = (1080, 1920) if kind == 'big' else (1920, 1080)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', AUDIO, '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-b:a', '192k', out], stdin=subprocess.PIPE)
    for f in range(N):
        tt = f / FPS; cv = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(cv)
        sub = next((s[2] for s in segs if s[0] <= tt <= s[1] + 0.3), '')
        if kind == 'big':
            d.rectangle((60, 120, W-60, 760), outline=(150, 145, 138), width=4)
            d.text((W/2, 440), '資訊窗（解題圖解）', fill=(150, 145, 138), font=font_small, anchor='mm')
            im, dy = avatar(f, 0.85, 'big'); cv.paste(im, ((W - im.width)//2, int(H - im.height + 30 + dy)), im)
            if sub: d.text((W/2, 860), sub, fill=(30, 28, 26), font=font_big, anchor='mm')
            if os.environ.get('POSE_DEBUG'): d.text((80, 1820), '姿勢：' + body_at(tt)[1], fill=(200, 40, 40), font=font_small)
        else:
            d.rectangle((0, 0, W, H), fill=(205, 200, 192))
            d.text((W/2, H/2-40), '故事段漫畫覆蓋（示意）', fill=(120, 115, 108), font=font_small, anchor='mm')
            im, dy = avatar(f, 0.82, 'small'); cv.paste(im, (W - im.width - 40, int(H - im.height + 6 + dy)), im)
            if sub: d.text((W/2-200, H-90), sub, fill=(30, 28, 26), font=font_small, anchor='mm')
        p.stdin.write(cv.tobytes())
    p.stdin.close(); p.wait()
print('pose switches', [(round(t, 2), p) for t, p in switches])
if os.environ.get('NECK_QC'):
    # 每個姿勢各取切入、淡化中點與切出一格；所有影格都從實際 avatar 合成路徑擷取。
    qc_names = [n for n in POSE_NAMES if n != '垂手']
    qc_font = ImageFont.truetype(FONT, 25)
    sheet = Image.new('RGB', (3*720, len(qc_names)*440), PAPER)
    for row, name in enumerate(qc_names):
        switches[:] = [(0.0, '垂手'), (1.0, name), (4.0, '垂手')]
        for col, (frame, label) in enumerate(((31, '切入'), (32, '淡化中間'), (123, '切出'))):
            im, _ = avatar(frame, 0.85, 'big')
            tile = Image.new('RGBA', im.size, PAPER + (255,)); tile.alpha_composite(im)
            crop = tile.crop((170, 350, 530, 550)).resize((720, 400), Image.Resampling.LANCZOS)
            sheet.paste(crop.convert('RGB'), (col*720, row*440+40))
            ImageDraw.Draw(sheet).text((col*720+10, row*440+5),
                                       f'{name} {label} {frame/FPS:.2f}s', fill=(35, 30, 27), font=qc_font)
    sheet.save(OUT + '-neck-qc-2x.png')
    sys.exit()
if os.environ.get('STILL'):  # 只出六種姿勢聯絡表，檢查頭身接縫
    tiles = []
    for n in POSE_NAMES:
        switches[:] = [(0.0, n)]; im, _ = avatar(60, 0.5, 'big')
        bg = Image.new('RGBA', im.size, PAPER + (255,)); bg.alpha_composite(im); ImageDraw.Draw(bg).text((10, 10), n, fill=(200, 40, 40), font=font_small); tiles.append(bg)
    sh = Image.new('RGB', (sum(t.width for t in tiles), tiles[0].height), 'white'); x = 0
    for t in tiles: sh.paste(t, (x, 0)); x += t.width
    sh.save(OUT + '-poses.png'); sys.exit()
for kind in os.environ.get('ONLY', 'big,small').split(','):
    render(kind, OUT + ('-big-9x16.mp4' if kind == 'big' else '-small-16x9.mp4'))
print('mouths', counts); print('nods', len(nods), 'tilts', len(tilts), 'blinks', len(blinks))
