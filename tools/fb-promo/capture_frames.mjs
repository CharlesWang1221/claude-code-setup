#!/usr/bin/env node
/**
 * FB 預告幀截圖
 * 用法: node capture_frames.mjs <html_path> <frames_dir> <duration_sec> [fps=24]
 */
import puppeteer from 'puppeteer';
import { mkdirSync } from 'fs';
import { resolve } from 'path';

const [,, htmlArg, framesArg, durationArg, fpsArg] = process.argv;
if (!htmlArg || !framesArg || !durationArg) {
  console.error('Usage: node capture_frames.mjs <html_path> <frames_dir> <duration_sec> [fps]');
  process.exit(1);
}

const HTML_PATH = resolve(htmlArg).replace(/\\/g, '/');
const FRAMES_DIR = resolve(framesArg);
const FPS = parseInt(fpsArg || '24', 10);
const DURATION = parseFloat(durationArg);
const TOTAL_FRAMES = Math.ceil(FPS * DURATION);
const W = 1080, H = 1920;

mkdirSync(FRAMES_DIR, { recursive: true });
console.log(`Capturing ${TOTAL_FRAMES} frames at ${FPS}fps (${W}×${H})...`);
console.log(`HTML: file:///${HTML_PATH}`);
console.log(`Output: ${FRAMES_DIR}`);

const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox','--disable-setuid-sandbox','--disable-web-security','--hide-scrollbars']
});
const page = await browser.newPage();
await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
await page.goto(`file:///${HTML_PATH}`);
await new Promise(r => setTimeout(r, 2000));

await page.evaluate(() => {
  window._manualTime = 0;
  const audio = document.getElementById('audio');
  if (audio) {
    Object.defineProperty(audio, 'currentTime', {
      get() { return window._manualTime || 0; },
      set(v) { window._manualTime = v; },
      configurable: true
    });
    Object.defineProperty(audio, 'paused', {
      get() { return false; },
      configurable: true
    });
  }
  const ov = document.getElementById('startOverlay');
  if (ov) ov.style.display = 'none';
  const ctrl = document.getElementById('controls');
  if (ctrl) ctrl.style.display = 'none';
  const prog = document.getElementById('progress-wrap');
  if (prog) prog.style.display = 'none';
});

await new Promise(r => setTimeout(r, 500));

const pad = n => String(n).padStart(5, '0');

for (let i = 0; i < TOTAL_FRAMES; i++) {
  const t = i / FPS;
  await page.evaluate((time) => { window._manualTime = time; }, t);
  await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.screenshot({ path: `${FRAMES_DIR}/frame_${pad(i)}.png`, type: 'png' });
  if (i % FPS === 0) process.stdout.write(`\r${i}/${TOTAL_FRAMES} (${t.toFixed(1)}s)   `);
}

await browser.close();
console.log(`\nDone → ${FRAMES_DIR}`);
