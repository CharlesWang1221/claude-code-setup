#!/usr/bin/env node
/**
 * IG 靜態圖片截圖
 * 用法: node capture_ig.mjs <html_path> <output_png> [width=1080] [height=1080]
 */
import puppeteer from 'puppeteer';
import { resolve, dirname } from 'path';
import { existsSync, mkdirSync } from 'fs';

const [,, htmlArg, outArg, wArg, hArg] = process.argv;
if (!htmlArg || !outArg) {
  console.error('Usage: node capture_ig.mjs <html_path> <output_png> [width] [height]');
  process.exit(1);
}

const HTML_PATH = resolve(htmlArg).replace(/\\/g, '/');
const OUT_PNG   = resolve(outArg);
const W = parseInt(wArg || '1080', 10);
const H = parseInt(hArg || '1080', 10);
const systemChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const chromeExecutable = process.env.CHROME_PATH || (existsSync(systemChrome) ? systemChrome : undefined);

mkdirSync(dirname(OUT_PNG), { recursive: true });

const launchOptions = {
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security', '--hide-scrollbars']
};
if (chromeExecutable) launchOptions.executablePath = chromeExecutable;

const browser = await puppeteer.launch(launchOptions);

try {
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
  await page.goto(`file:///${HTML_PATH}`, { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 400));
  await page.screenshot({ path: OUT_PNG, clip: { x: 0, y: 0, width: W, height: H } });
  console.log(`  ✅ ${OUT_PNG}`);
} finally {
  await browser.close();
}
