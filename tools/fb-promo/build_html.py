#!/usr/bin/env python3
"""
FB 預告 HTML 產生器
用法: python build_html.py <episode_dir> <output_html>
範例: python build_html.py ../../video-projects/s2ep7-short /tmp/explainer.html
"""
import base64, os, sys, json, re

if len(sys.argv) < 3:
    print("Usage: python build_html.py <episode_dir> <output_html>")
    sys.exit(1)

EP_DIR = sys.argv[1]
OUT_HTML = sys.argv[2]

# 讀音訊
audio_path = os.path.join(EP_DIR, '03-edited', 'edited.mp4')
if not os.path.exists(audio_path):
    print(f"ERROR: {audio_path} not found")
    sys.exit(1)

# 用 FFmpeg 先抽成 MP3
import subprocess, tempfile
tmp_mp3 = os.path.join(tempfile.gettempdir(), 'fb_promo_audio.mp3')
subprocess.run([
    'ffmpeg', '-y', '-i', audio_path,
    '-vn', '-ac', '1', '-ab', '64k', '-ar', '44100', '-f', 'mp3', tmp_mp3
], check=True, capture_output=True)

with open(tmp_mp3, 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
os.unlink(tmp_mp3)

# 讀 SRT 字幕
srt_path = os.path.join(EP_DIR, '02-transcript', 'edited.srt')
subs_js = '[]'
if os.path.exists(srt_path):
    def srt_to_sec(ts):
        h, m, rest = ts.split(':')
        s, ms = rest.replace(',', '.').split('.')
        return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000
    subs = []
    with open(srt_path, encoding='utf-8') as f:
        blocks = f.read().strip().split('\n\n')
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            times = lines[1].split(' --> ')
            start = srt_to_sec(times[0].strip())
            end   = srt_to_sec(times[1].strip())
            text  = ' '.join(lines[2:])
            subs.append({'s': round(start, 3), 'e': round(end, 3), 't': text})
    subs_js = json.dumps(subs, ensure_ascii=False)

# 讀標題
title = '不標準答案'
title_path = os.path.join(EP_DIR, '06-publish', 'title.txt')
if os.path.exists(title_path):
    with open(title_path, encoding='utf-8') as f:
        title = f.read().strip().split('\n')[0]

# 讀音訊時長
probe = subprocess.run(
    ['ffprobe', '-v', 'quiet', '-show_format', '-print_format', 'json', audio_path],
    capture_output=True, text=True
)
duration = float(json.loads(probe.stdout)['format']['duration'])
dur_fmt = f"0:{int(duration%60):02d}"

# 偵測 ep 名稱
ep_name = os.path.basename(EP_DIR.rstrip('/\\'))
ep_label = ep_name.replace('-short', '').upper().replace('S', 'S').replace('EP', ' EP')

# 計算場景（6 等分）
n_scenes = 6
scene_dur = duration / n_scenes
scenes_js = json.dumps([
    {'start': round(i * scene_dur, 3), 'end': round((i+1) * scene_dur, 3)}
    for i in range(n_scenes)
], ensure_ascii=False)

html = f"""<title>{title} — 不標準答案</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#F9F7F7;--bg2:#EEF1F7;--card:#fff;
  --teal:#3F72AF;--teal-soft:rgba(63,114,175,0.08);
  --coral:#E07A5F;--coral-soft:rgba(224,122,95,0.08);
  --navy:#112D4E;--muted:rgba(17,45,78,0.65);
  --border:rgba(17,45,78,0.08);--shadow:0 4px 28px rgba(17,45,78,0.09);
  --font-heading:"PMingLiU","DFKai-SB","Songti TC",serif;
  --font-body:"Microsoft JhengHei","PingFang TC",sans-serif;
  --font-mono:"Consolas","Courier New",monospace;
}}
html,body{{width:100%;height:100%;background:var(--bg);color:var(--navy);font-family:var(--font-body);overflow:hidden;}}
#ambient{{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;}}
.pt{{position:absolute;border-radius:50%;background:var(--teal-soft);animation:drift linear infinite;}}
.bg-blob{{position:absolute;border-radius:50%;filter:blur(120px);animation:blobDrift ease-in-out infinite alternate;}}
#sceneFlash{{position:fixed;inset:0;pointer-events:none;z-index:5;background:radial-gradient(circle at 50% 40%,rgba(63,114,175,0.18) 0%,transparent 65%);opacity:0;transition:opacity 0.3s;}}
@keyframes drift{{0%{{transform:translateY(110vh) rotate(0deg)}}100%{{transform:translateY(-20px) rotate(360deg)}}}}
@keyframes blobDrift{{0%{{transform:translate(0,0) scale(1)}}100%{{transform:translate(40px,60px) scale(1.3)}}}}
#stage{{position:fixed;top:0;left:0;right:0;bottom:56px;perspective:2000px;overflow:hidden;z-index:1;}}
.scene{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;padding:60px 48px 32px;opacity:0;pointer-events:none;transform:scale(0.96) translateZ(-40px);transition:opacity 0.6s cubic-bezier(.4,0,.2,1),transform 0.6s cubic-bezier(.4,0,.2,1);will-change:opacity,transform;}}
.scene.active{{opacity:1;pointer-events:auto;transform:scale(1) translateZ(0);}}
.scene.zoom-out{{opacity:0;transform:scale(1.04) translateZ(40px);transition:opacity 0.4s,transform 0.4s;}}
[data-at]{{opacity:0;transform:translateY(18px);transition:opacity 0.55s ease,transform 0.55s ease;}}
[data-at].revealed{{opacity:1;transform:translateY(0);}}
.eyebrow{{display:flex;align-items:center;gap:10px;font-family:var(--font-mono);font-size:13px;letter-spacing:0.18em;text-transform:uppercase;color:var(--teal);}}
.eyebrow::before,.eyebrow::after{{content:"";flex:0 0 28px;height:1px;background:var(--teal);opacity:0.4;}}
.title{{font-family:var(--font-heading);font-size:52px;font-weight:900;color:var(--navy);line-height:1.2;text-align:center;text-wrap:balance;}}
.title .hl{{color:var(--teal);}}
.note{{font-family:var(--font-body);font-size:22px;color:var(--muted);max-width:800px;text-align:center;line-height:1.75;}}
.cam-wrap{{width:180px;height:180px;perspective:700px;}}
.cam-inner{{width:100%;height:100%;position:relative;transform-style:preserve-3d;animation:camSpin 8s linear infinite;}}
.cam-face{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:var(--card);border-radius:24px;box-shadow:var(--shadow);border:1px solid var(--border);font-size:72px;backface-visibility:hidden;}}
.cam-face.back{{transform:rotateY(180deg);font-size:56px;background:var(--teal-soft);}}
@keyframes camSpin{{0%{{transform:rotateY(0deg) rotateX(12deg)}}100%{{transform:rotateY(360deg) rotateX(12deg)}}}}
.flip-wrap{{width:220px;height:180px;perspective:800px;}}
.flip-inner{{width:100%;height:100%;position:relative;transform-style:preserve-3d;animation:flipLoop 5s ease-in-out infinite;}}
.flip-front,.flip-back{{position:absolute;inset:0;backface-visibility:hidden;border-radius:24px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;background:var(--card);box-shadow:var(--shadow);border:1px solid var(--border);font-size:18px;color:var(--muted);}}
.flip-back{{transform:rotateY(180deg);background:var(--coral-soft);border-color:rgba(224,122,95,0.28);color:var(--coral);}}
.big-icon{{font-size:56px;}}
@keyframes flipLoop{{0%,38%{{transform:rotateY(0deg)}}50%,88%{{transform:rotateY(180deg)}}100%{{transform:rotateY(360deg)}}}}
.layers-wrap{{position:relative;width:520px;height:160px;perspective:700px;}}
.layer{{position:absolute;left:0;right:0;height:48px;background:var(--card);border-radius:14px;box-shadow:var(--shadow);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;gap:14px;font-size:18px;color:var(--muted);}}
.layer:nth-child(1){{top:0;animation:lf1 3s ease-in-out infinite alternate;}}
.layer:nth-child(2){{top:56px;animation:lf2 4s ease-in-out infinite alternate;}}
.layer:nth-child(3){{top:112px;background:var(--coral-soft);border-color:rgba(224,122,95,0.22);color:var(--coral);animation:lf3 5s ease-in-out infinite alternate;}}
@keyframes lf1{{0%{{transform:translateZ(30px) rotateX(8deg)}}100%{{transform:translateZ(30px) rotateX(8deg) translateY(-8px)}}}}
@keyframes lf2{{0%{{transform:translateZ(0) rotateX(8deg)}}100%{{transform:translateZ(0) rotateX(8deg) translateY(-6px)}}}}
@keyframes lf3{{0%{{transform:translateZ(-30px) rotateX(8deg)}}100%{{transform:translateZ(-30px) rotateX(8deg) translateY(-4px)}}}}
.orbit-wrap{{position:relative;width:240px;height:240px;}}
.orbit-center{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:56px;z-index:2;}}
.orbit-ring{{position:absolute;inset:14px;border:2px dashed rgba(63,114,175,0.32);border-radius:50%;animation:oSpin 5s linear infinite;}}
.orbit-ring-outer{{position:absolute;inset:-16px;border:2px dashed rgba(224,122,95,0.22);border-radius:50%;animation:oSpin 9s linear infinite reverse;}}
.orbit-dot{{position:absolute;top:-12px;left:50%;transform:translateX(-50%);width:28px;height:28px;border-radius:50%;background:var(--teal);display:flex;align-items:center;justify-content:center;font-size:14px;color:#fff;box-shadow:0 3px 14px rgba(63,114,175,0.45);}}
.orbit-dot-outer{{position:absolute;top:-10px;left:50%;transform:translateX(-50%);width:24px;height:24px;border-radius:50%;background:var(--coral);display:flex;align-items:center;justify-content:center;font-size:12px;color:#fff;box-shadow:0 3px 14px rgba(224,122,95,0.45);}}
@keyframes oSpin{{0%{{transform:rotate(0)}}100%{{transform:rotate(360deg)}}}}
.ba-wrap{{display:flex;gap:24px;}}
.ba-panel{{width:200px;height:160px;border-radius:24px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;font-size:15px;font-family:var(--font-mono);letter-spacing:0.04em;box-shadow:var(--shadow);border:1px solid var(--border);}}
.ba-panel .panel-icon{{font-size:44px;}}
.ba-panel.before{{background:var(--card);color:var(--muted);animation:pB 3.5s ease-in-out infinite alternate;}}
.ba-panel.after{{background:var(--coral-soft);color:var(--coral);border-color:rgba(224,122,95,0.28);animation:pA 4.2s ease-in-out infinite alternate;}}
@keyframes pB{{0%{{transform:rotateY(-14deg) rotateX(5deg)}}100%{{transform:rotateY(-14deg) rotateX(5deg) translateY(-10px)}}}}
@keyframes pA{{0%{{transform:rotateY(14deg) rotateX(-5deg)}}100%{{transform:rotateY(14deg) rotateX(-5deg) translateY(-10px)}}}}
.phone-wrap{{perspective:700px;}}
.phone{{width:150px;height:256px;border-radius:32px;background:var(--navy);border:3px solid rgba(255,255,255,0.07);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;box-shadow:0 32px 80px rgba(17,45,78,0.35);animation:phoneFloat 4s ease-in-out infinite alternate;position:relative;overflow:hidden;}}
.phone::before{{content:"";position:absolute;top:14px;width:56px;height:5px;background:rgba(255,255,255,0.1);border-radius:3px;}}
.phone-logo{{font-size:44px;}}
.phone-title{{font-family:var(--font-heading);font-size:15px;color:#fff;text-align:center;padding:0 12px;line-height:1.4;}}
.phone-ep{{font-family:var(--font-mono);font-size:11px;color:rgba(255,255,255,0.4);letter-spacing:0.14em;}}
@keyframes phoneFloat{{0%{{transform:rotateY(-14deg) rotateX(6deg)}}100%{{transform:rotateY(14deg) rotateX(-6deg) translateY(-18px)}}}}
#controls{{position:fixed;bottom:0;left:0;right:0;height:56px;background:rgba(249,247,247,0.95);backdrop-filter:blur(16px);border-top:1px solid var(--border);display:flex;align-items:center;gap:12px;padding:0 20px;z-index:10;}}
.cb{{background:none;border:none;cursor:pointer;color:var(--navy);font-size:20px;padding:6px 8px;border-radius:8px;line-height:1;flex-shrink:0;transition:background 0.15s,color 0.15s;}}
.cb:hover,.cb:focus-visible{{background:var(--teal-soft);color:var(--teal);outline:none;}}
.cb.on{{color:var(--teal);}}
#cap{{flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-size:15px;color:var(--muted);min-width:0;}}
#cap.cap-in{{animation:capIn 0.22s ease;}}
@keyframes capIn{{0%{{opacity:0;transform:translateY(4px)}}100%{{opacity:1;transform:translateY(0)}}}}
#timer{{flex-shrink:0;font-family:var(--font-mono);font-size:13px;color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums;}}
#progress-wrap{{position:fixed;bottom:56px;left:0;right:0;height:4px;background:var(--border);z-index:10;cursor:pointer;}}
#progress-bar{{height:100%;background:var(--teal);width:0%;}}
.ch-dot{{position:absolute;top:-4px;width:12px;height:12px;border-radius:50%;background:var(--bg2);border:2px solid var(--teal);transform:translateX(-50%);pointer-events:none;transition:background 0.2s;}}
.ch-dot.past{{background:var(--teal);}}
.ch-dot.next{{animation:dotPulse 1.2s ease-in-out infinite;}}
@keyframes dotPulse{{0%,100%{{box-shadow:0 0 0 0 rgba(63,114,175,0.5)}}50%{{box-shadow:0 0 0 5px rgba(63,114,175,0)}}}}
#startOverlay{{position:fixed;inset:0;z-index:20;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px;background:rgba(249,247,247,0.93);backdrop-filter:blur(10px);cursor:pointer;}}
#startOverlay .play-btn{{width:96px;height:96px;border-radius:50%;background:var(--teal);display:flex;align-items:center;justify-content:center;box-shadow:0 10px 40px rgba(63,114,175,0.4);transition:transform 0.15s;}}
#startOverlay .play-btn:hover{{transform:scale(1.08);}}
#startOverlay .play-btn svg{{fill:#fff;margin-left:6px;}}
#startOverlay p{{font-family:var(--font-mono);font-size:14px;letter-spacing:0.14em;text-transform:uppercase;color:var(--muted);}}
@media(prefers-reduced-motion:reduce){{
  .pt,.bg-blob,.cam-inner,.flip-inner,.orbit-ring,.orbit-ring-outer,.ba-panel,.phone,.layer{{animation:none!important;}}
  .scene{{transition:opacity 0.15s!important;}}
  [data-at]{{transition:opacity 0.15s!important;}}
}}
</style>

<audio id="audio" preload="auto">
  <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
</audio>

<div id="ambient"></div>
<div id="sceneFlash"></div>

<div id="startOverlay">
  <div class="play-btn">
    <svg width="36" height="36" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
  </div>
  <p>點擊播放</p>
</div>

<div id="stage">
  <div class="scene" id="s0">
    <div class="eyebrow" data-at="0.3">{ep_label} · 不標準答案</div>
    <div class="cam-wrap" data-at="0.9">
      <div class="cam-inner"><div class="cam-face">📷</div><div class="cam-face back">🔍</div></div>
    </div>
    <div class="title" data-at="2">節目<span class="hl">重點場景</span></div>
    <div class="note" data-at="3.2">從這集開始聽</div>
  </div>
  <div class="scene" id="s1">
    <div class="eyebrow" data-at="0.3">場景一</div>
    <div class="flip-wrap" data-at="0.9">
      <div class="flip-inner">
        <div class="flip-front"><div class="big-icon">💬</div><span>問題</span></div>
        <div class="flip-back"><div class="big-icon">💡</div><span>答案</span></div>
      </div>
    </div>
    <div class="title" data-at="2">觀點<span class="hl">不一樣</span></div>
    <div class="note" data-at="3.2">不標準的對話，才有標準答不了的問題</div>
  </div>
  <div class="scene" id="s2">
    <div class="eyebrow" data-at="0.3">場景二</div>
    <div class="layers-wrap" data-at="0.9">
      <div class="layer"><span>🎙</span><span>主持人</span></div>
      <div class="layer"><span>🎧</span><span>聽眾</span></div>
      <div class="layer"><span>🌐</span><span>議題</span></div>
    </div>
    <div class="title" data-at="2">對話<span class="hl">有深度</span></div>
    <div class="note" data-at="3.2">每集一個不標準的問題</div>
  </div>
  <div class="scene" id="s3">
    <div class="eyebrow" data-at="0.3">場景三</div>
    <div class="orbit-wrap" data-at="0.9">
      <div class="orbit-center">🎯</div>
      <div class="orbit-ring"><div class="orbit-dot">💭</div></div>
      <div class="orbit-ring-outer"><div class="orbit-dot-outer">✨</div></div>
    </div>
    <div class="title" data-at="2">視角<span class="hl">很多元</span></div>
    <div class="note" data-at="3.2">繞著同一個核心，看不同的切入點</div>
  </div>
  <div class="scene" id="s4">
    <div class="eyebrow" data-at="0.3">場景四</div>
    <div class="ba-wrap" data-at="0.9">
      <div class="ba-panel before"><div class="panel-icon">🤔</div><span>以前覺得</span><span>很正常</span></div>
      <div class="ba-panel after"><div class="panel-icon">💥</div><span>聽完才發現</span><span>不一樣</span></div>
    </div>
    <div class="title" data-at="2">聽完<span class="hl">想法變了</span></div>
    <div class="note" data-at="3.2">這就是不標準答案存在的原因</div>
  </div>
  <div class="scene" id="s5">
    <div class="eyebrow" data-at="0.3">不標準答案</div>
    <div class="phone-wrap" data-at="0.9">
      <div class="phone">
        <div class="phone-logo">🎙</div>
        <div class="phone-title">不標準答案</div>
        <div class="phone-ep">{ep_label}</div>
      </div>
    </div>
    <div class="title" data-at="2">現在就<span class="hl">開始聽</span></div>
    <div class="note" data-at="3.2">追蹤《不標準答案》Podcast<br>每集都有新的不標準</div>
  </div>
</div>

<div id="progress-wrap"><div id="progress-bar"></div></div>
<div id="controls">
  <button class="cb" id="btnPrev">◀</button>
  <button class="cb on" id="btnPlay">▶</button>
  <button class="cb" id="btnNext">▶▶</button>
  <span id="cap"></span>
  <span id="timer">0:00 / {dur_fmt}</span>
</div>

<script>
const TOTAL={round(duration, 3)};
const scenes={scenes_js};
const subs={subs_js};
const audio=document.getElementById('audio');
const sceneEls=scenes.map((_,i)=>document.getElementById('s'+i));
const progressBar=document.getElementById('progress-bar');
const progressWrap=document.getElementById('progress-wrap');
const capEl=document.getElementById('cap');
const timerEl=document.getElementById('timer');
const btnPlay=document.getElementById('btnPlay');
const btnPrev=document.getElementById('btnPrev');
const btnNext=document.getElementById('btnNext');
const flash=document.getElementById('sceneFlash');
const overlay=document.getElementById('startOverlay');
let currentScene=0,currentSub=-1;
function fmtTime(s){{const m=Math.floor(s/60),sec=Math.floor(s%60);return m+':'+(sec<10?'0':'')+sec;}}
function setScene(idx){{
  const prev=currentScene;
  currentScene=Math.max(0,Math.min(scenes.length-1,idx));
  if(prev!==currentScene){{
    sceneEls[prev].classList.remove('active');sceneEls[prev].classList.add('zoom-out');
    setTimeout(()=>sceneEls[prev].classList.remove('zoom-out'),500);
    flash.style.opacity='1';setTimeout(()=>flash.style.opacity='0',350);
  }}
  sceneEls[currentScene].classList.add('active');
  sceneEls[currentScene].querySelectorAll('[data-at]').forEach(el=>el.classList.remove('revealed'));
  updateDots();
}}
function tick(){{
  const t=audio.currentTime;
  let si=scenes.findIndex((s,i)=>{{const nx=i+1<scenes.length?scenes[i+1].start:TOTAL+1;return t>=s.start&&t<nx;}});
  if(si<0) si=scenes.length-1;
  if(si!==currentScene) setScene(si);
  const localT=t-scenes[currentScene].start;
  sceneEls[currentScene].querySelectorAll('[data-at]').forEach(el=>{{
    if(localT>=parseFloat(el.dataset.at)) el.classList.add('revealed');
    else el.classList.remove('revealed');
  }});
  const si2=subs.findIndex(sub=>t>=sub.s&&t<sub.e);
  if(si2!==currentSub){{
    currentSub=si2;const txt=si2>=0?subs[si2].t:'';
    if(txt!==capEl.textContent){{capEl.textContent=txt;capEl.classList.remove('cap-in');void capEl.offsetWidth;capEl.classList.add('cap-in');}}
  }}
  progressBar.style.width=(t/TOTAL*100)+'%';
  timerEl.textContent=fmtTime(t)+' / '+fmtTime(TOTAL);
  updateDots();requestAnimationFrame(tick);
}}
function updateDots(){{
  const t=audio.currentTime;
  document.querySelectorAll('.ch-dot').forEach((dot,i)=>{{
    dot.classList.remove('past','next');
    if(t>=scenes[i].start) dot.classList.add('past');
    else if(i===currentScene+1) dot.classList.add('next');
  }});
}}
overlay.addEventListener('click',()=>{{audio.play().then(()=>{{overlay.style.display='none';}});}});
btnPlay.addEventListener('click',()=>{{if(audio.paused){{audio.play();}}else{{audio.pause();}}}});
audio.addEventListener('play',()=>{{btnPlay.textContent='⏸';btnPlay.classList.add('on');}});
audio.addEventListener('pause',()=>{{btnPlay.textContent='▶';btnPlay.classList.remove('on');}});
audio.addEventListener('ended',()=>{{btnPlay.textContent='▶';btnPlay.classList.remove('on');}});
btnPrev.addEventListener('click',()=>{{if(currentScene>0){{audio.currentTime=scenes[currentScene-1].start;setScene(currentScene-1);}}else audio.currentTime=0;}});
btnNext.addEventListener('click',()=>{{if(currentScene<scenes.length-1){{audio.currentTime=scenes[currentScene+1].start;setScene(currentScene+1);}}}});
progressWrap.addEventListener('click',e=>{{const r=progressWrap.getBoundingClientRect();audio.currentTime=Math.max(0,Math.min(TOTAL,(e.clientX-r.left)/r.width*TOTAL));}});
document.addEventListener('keydown',e=>{{if(e.key===' '){{e.preventDefault();btnPlay.click();}}if(e.key==='ArrowLeft')btnPrev.click();if(e.key==='ArrowRight')btnNext.click();}});
let tx=0;
document.addEventListener('touchstart',e=>tx=e.touches[0].clientX,{{passive:true}});
document.addEventListener('touchend',e=>{{const dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>50){{dx<0?btnNext.click():btnPrev.click();}}}},{{passive:true}});
const amb=document.getElementById('ambient');
for(let i=0;i<18;i++){{
  const p=document.createElement('div');p.className='pt';const sz=4+Math.random()*12;
  p.style.cssText='width:'+sz+'px;height:'+sz+'px;left:'+(Math.random()*100)+'%;bottom:-20px;animation-duration:'+(10+Math.random()*14)+'s;animation-delay:-'+(Math.random()*18)+'s;opacity:'+(0.2+Math.random()*0.4)+';';
  amb.appendChild(p);
}}
for(let i=0;i<2;i++){{
  const b=document.createElement('div');b.className='bg-blob';
  b.style.cssText='width:'+(400+i*160)+'px;height:'+(400+i*160)+'px;'+(i===0?'left:-120px;top:-120px':'right:-120px;bottom:-120px')+';background:'+(i===0?'rgba(63,114,175,0.06)':'rgba(224,122,95,0.04)')+';animation-duration:'+(8+i*5)+'s;';
  amb.appendChild(b);
}}
scenes.forEach((s,i)=>{{
  const dot=document.createElement('div');dot.className='ch-dot';
  dot.style.left=(s.start/TOTAL*100)+'%';progressWrap.appendChild(dot);
}});
setScene(0);requestAnimationFrame(tick);
</script>"""

with open(OUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML written: {OUT_HTML} ({os.path.getsize(OUT_HTML)//1024}KB)")
