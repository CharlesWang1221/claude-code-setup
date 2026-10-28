"""嘴型元件（開講試點 v7）：words.json + 音檔 + 角色前視圖 → 大／小兩種尺寸 MP4。"""
import sys, json, math, random, subprocess, re, wave
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
def with_mouth(name):
    f = base.copy()
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
CROPS = {'big': (90, 180, 910, 1310), 'small': (110, 190, 870, 1060)}  # small＝腰上鏡位
# 去背：從畫面四角往內 flood fill 亮色紙底，剩下的就是人物
_g = base.convert('L').point(lambda v: 255 if v > 205 else 0)
for seed in [(5, 5), (base.width-6, 5), (5, base.height-6), (base.width-6, base.height-6), (base.width//2, 5)]:
    ImageDraw.floodfill(_g, seed, 128)
CUT = Image.fromarray(np.where(np.asarray(_g) == 128, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))
# ---- 手臂圖層：以肩膀為軸心，只往外擺（左手順時針、右手逆時針）
ARM_L = [(185, 770), (255, 790), (296, 830), (300, 1170), (270, 1290), (120, 1290), (95, 1100), (110, 900), (140, 810)]
CORE_X = 262  # 身體側線保留在底圖，手臂挖空只到這裡
MIRROR = 1000
def poly_mask(pts, clip_x=None, right=False):
    m = Image.new('L', base.size, 0)
    q = [(min(x, clip_x), y) for x, y in pts] if clip_x else pts
    if right: q = [(MIRROR - x, y) for x, y in q]
    ImageDraw.Draw(m).polygon(q, fill=255); return m.filter(ImageFilter.GaussianBlur(2))
ARM_MASK = {'L': poly_mask(ARM_L), 'R': poly_mask(ARM_L, right=True)}
CORE = Image.fromarray(np.maximum(np.asarray(poly_mask(ARM_L, CORE_X)), np.asarray(poly_mask(ARM_L, CORE_X, True))))
PIVOT = {'L': (215, 800), 'R': (MIRROR - 215, 800)}
SIGN = {'L': -1, 'R': 1}
BODY_A = Image.fromarray((np.asarray(CUT).astype(float) * (1 - np.asarray(CORE) / 255)).astype(np.uint8))
ARMS = {}
for k in 'LR':
    a = base.convert('RGBA'); a.putalpha(Image.fromarray(np.minimum(np.asarray(CUT), np.asarray(ARM_MASK[k]))))
    ARMS[k] = a

# ---- 字 → 嘴型
def viseme(ch):
    if not re.match(r'[一-鿿]', ch): return None
    p = pinyin(ch, style=Style.NORMAL, strict=False)[0][0]
    ini = pinyin(ch, style=Style.INITIALS, strict=False)[0][0]
    fin = p[len(ini):] if p.startswith(ini) else p
    lip = ini in ('b', 'p', 'm')
    if ini in ('zh', 'ch', 'sh', 'r', 'z', 'c', 's') and fin == 'i': v = '扁'
    elif fin.endswith(('a', 'an', 'ang', 'ao')): v = '大開'
    elif fin in ('o', 'uo', 'ou', 'iu', 'ong', 'iong', 'u', 'v', 'un', 'vn', 'ue', 've') or fin.startswith('u'): v = '圓'
    elif fin.startswith('i') or fin in ('ai', 'ei', 'in', 'ing'): v = '扁'
    else: v = '小開'
    return lip, v
words = json.load(open(WORDS))
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', WAV]))
N = int(dur * FPS)
track = ['閉'] * N
for w in words:
    chars = [c for c in w['w'] if viseme(c)]
    if not chars: continue
    span = max(w['e'] - w['s'], 0.08) / len(chars)
    for k, c in enumerate(chars):
        lip, v = viseme(c); s = w['s'] + k * span; e = s + span
        for f in range(int(s * FPS), min(N, int(e * FPS) + 1)):
            t = (f / FPS - s) / span
            track[f] = '抿' if lip and t < 0.3 else ('小開' if t > 0.8 and v == '大開' else v)

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

env = rms / (rms.max() + 1e-9)
env = np.convolve(env, np.ones(9) / 9, 'same')  # 約 0.3 秒平滑，避免手抖
def arm_angle(f, k):
    ph = 0 if k == 'L' else 1.7
    sway = 0.6 * (1 + math.sin(f / FPS * 2 * math.pi / 4.2 + ph))
    beat = sum(1.6 * math.exp(-((f - n) / 6) ** 2) for n in nods) * (1 if k == 'L' else 0.7)
    return 0.0  # 2026-10-28 老查判定手臂切層擺動破圖，停用；手勢改走姿勢圖
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
    body = frames[(mouth, b)].convert('RGBA'); body.putalpha(BODY_A)
    for k in 'LR':
        arm = ARMS[k].rotate(SIGN[k] * arm_angle(f, k), resample=Image.BICUBIC, center=PIVOT[k])
        body.alpha_composite(arm)
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
        else:
            d.rectangle((0, 0, W, H), fill=(205, 200, 192))
            d.text((W/2, H/2-40), '故事段漫畫覆蓋（示意）', fill=(120, 115, 108), font=font_small, anchor='mm')
            im, dy = avatar(f, 0.70, 'small'); cv.paste(im, (W - im.width - 40, int(H - im.height + 6 + dy)), im)
            if sub: d.text((W/2-200, H-90), sub, fill=(30, 28, 26), font=font_small, anchor='mm')
        p.stdin.write(cv.tobytes())
    p.stdin.close(); p.wait()
import os
if os.environ.get('STILL'):
    _aa = arm_angle; tiles = []
    for deg in (0, 2.5, 5):
        arm_angle = lambda f, k, d=deg: d
        im, _ = avatar(60, 0.5, 'big'); bg = Image.new('RGBA', im.size, PAPER + (255,)); bg.alpha_composite(im); tiles.append(bg)
    sh = Image.new('RGB', (sum(t.width for t in tiles), tiles[0].height), 'white'); x = 0
    for t in tiles: sh.paste(t, (x, 0)); x += t.width
    sh.save(OUT + '-arms.png'); sys.exit()
render('big', OUT + '-big-9x16.mp4'); render('small', OUT + '-small-16x9.mp4')
from collections import Counter; print('mouths', Counter(track)); print('nods', len(nods), 'tilts', len(tilts), 'blinks', len(blinks))
