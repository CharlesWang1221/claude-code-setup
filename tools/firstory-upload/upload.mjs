/**
 * Firstory Studio 半自動上傳
 * 用法: node upload.mjs --episode s2ep8 --audio "C:\Users\...\audio.mp3"
 *
 * 流程：
 * 1. 開啟 Firstory Studio（保留登入狀態，只需首次手動登入）
 * 2. 自動填入標題、節目介紹、上傳音檔
 * 3. 停在發布頁讓你確認後手動點發布
 */
import { chromium } from 'playwright';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import { resolve, join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ── 解析參數 ─────────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
const getArg = (name) => { const i = argv.indexOf(`--${name}`); return i !== -1 ? argv[i + 1] : null; };

const epSlug  = getArg('episode');
const audio   = getArg('audio');

if (!epSlug) {
  console.error('Usage: node upload.mjs --episode <slug> [--audio <path>]');
  console.error('Example: node upload.mjs --episode s2ep8 --audio "C:\\Users\\siming_wang\\Downloads\\s2ep8.mp3"');
  process.exit(1);
}

const ROOT    = 'D:\\hot data\\CCoode';
const EP_DIR  = join(ROOT, 'output', `ep-${epSlug}`);
const SESSION = join(__dirname, 'browser-session');

mkdirSync(SESSION, { recursive: true });

// ── 讀取集數內容 ──────────────────────────────────────────────────────────────
const notesPath = join(EP_DIR, 'show-notes.md');
if (!existsSync(notesPath)) {
  console.error(`找不到 show-notes.md: ${notesPath}`);
  process.exit(1);
}

const md = readFileSync(notesPath, 'utf-8');

// 標題
const h1 = (md.match(/^# (.+)$/m) || [])[1] || epSlug;
const epM = h1.match(/(S\d+EP?\d+)\s*[—–\-]+\s*(.+)/i);
let title, epNum;
if (epM) {
  epNum  = epM[1].toUpperCase().replace(/EP?(\d)$/, 'E0$1').replace(/EP?(\d{2,})$/, 'E$1');
  title  = `${epM[2].trim()}｜不標準答案 ${epNum}`;
} else {
  title  = h1;
  epNum  = '';
}

// Show Notes 純文字版（Firstory 說明欄）
const showNotes = md
  .replace(/^#+ .+$/gm, '')           // 移除標題行
  .replace(/\*\*(.+?)\*\*/g, '$1')    // bold
  .replace(/^>\s*/gm, '')             // blockquote
  .replace(/^-\s+/gm, '• ')           // list
  .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // links
  .replace(/\n{3,}/g, '\n\n')
  .trim();

console.log(`\n=== Firstory 上傳 — ep-${epSlug} ===`);
console.log(`標題: ${title}`);
if (audio) console.log(`音檔: ${audio}`);
console.log('');

// ── 啟動瀏覽器 ────────────────────────────────────────────────────────────────
const ctx = await chromium.launchPersistentContext(SESSION, {
  headless: false,
  viewport: { width: 1400, height: 900 },
  locale: 'zh-TW',
});

const page = await ctx.newPage();
await page.goto('https://studio.firstory.me', { waitUntil: 'domcontentloaded', timeout: 30000 });

// ── 登入檢查 ──────────────────────────────────────────────────────────────────
if (page.url().includes('login') || page.url().includes('signin')) {
  console.log('>>> 請在瀏覽器視窗中登入 Firstory Studio（只需一次，之後會記住）');
  console.log('>>> 等待登入中...');
  await page.waitForURL(url => !url.includes('login') && !url.includes('signin'), { timeout: 120000 });
  console.log('登入成功！\n');
}

// ── 前往新增集數頁 ────────────────────────────────────────────────────────────
console.log('前往新增集數頁...');
await page.goto('https://studio.firstory.me/episodes/create', {
  waitUntil: 'networkidle', timeout: 30000
});
await page.waitForTimeout(1500);

// ── 截圖看頁面結構（首次執行時診斷用）────────────────────────────────────────
const screenshotPath = join(EP_DIR, 'firstory-screenshot.png');
await page.screenshot({ path: screenshotPath, fullPage: false });
console.log(`頁面截圖已存至: ${screenshotPath}`);

// ── 填入標題 ──────────────────────────────────────────────────────────────────
console.log('填入標題...');
const titleSel = [
  'input[name="title"]',
  'input[placeholder*="標題"]',
  'input[placeholder*="title" i]',
  'input[type="text"]',
].join(', ');

try {
  const titleEl = page.locator(titleSel).first();
  await titleEl.waitFor({ timeout: 8000 });
  await titleEl.click();
  await titleEl.fill(title);
  console.log(`  ✓ 標題: ${title}`);
} catch {
  console.warn('  ! 找不到標題欄位，請手動填入');
}

// ── 填入節目介紹 ──────────────────────────────────────────────────────────────
console.log('填入節目介紹...');
try {
  // 優先嘗試 Quill 富文字編輯器
  const quill = page.locator('.ql-editor').first();
  const hasQuill = await quill.isVisible().catch(() => false);

  if (hasQuill) {
    await quill.click();
    await quill.fill(showNotes);
    console.log('  ✓ Show Notes（Quill 編輯器）');
  } else {
    // 嘗試一般 textarea
    const textSel = [
      'textarea[name="description"]',
      'textarea[placeholder*="介紹"]',
      'textarea[placeholder*="description" i]',
      '[contenteditable="true"]',
    ].join(', ');
    const textEl = page.locator(textSel).first();
    await textEl.waitFor({ timeout: 5000 });
    await textEl.click();
    await textEl.fill(showNotes);
    console.log('  ✓ Show Notes（textarea）');
  }
} catch {
  // 最後手段：剪貼板貼上
  console.warn('  ! 自動填入失敗，嘗試剪貼板...');
  await page.evaluate((text) => navigator.clipboard.writeText(text), showNotes);
  const notesEl = page.locator('[contenteditable="true"]').first();
  if (await notesEl.isVisible().catch(() => false)) {
    await notesEl.click();
    await page.keyboard.press('Control+a');
    await page.keyboard.press('Control+v');
    console.log('  ✓ Show Notes（剪貼板）');
  } else {
    console.warn('  ! 請手動貼上節目介紹');
  }
}

// ── 上傳音檔 ──────────────────────────────────────────────────────────────────
if (audio) {
  if (!existsSync(audio)) {
    console.warn(`  ! 找不到音檔: ${audio}`);
  } else {
    console.log('上傳音檔...');
    try {
      const fileInput = page.locator('input[type="file"][accept*="audio"]').first()
        .or(page.locator('input[type="file"]').first());
      await fileInput.setInputFiles(audio);
      console.log('  ✓ 音檔已設定，等待上傳...');
      // 等待上傳進度（最多 5 分鐘）
      await page.waitForFunction(
        () => !document.querySelector('[class*="progress"][style*="width"]') ||
              document.querySelector('[class*="progress"]')?.style?.width === '100%',
        { timeout: 300000 }
      ).catch(() => console.log('  (上傳進度偵測逾時，請自行確認上傳完成)'));
    } catch {
      console.warn('  ! 找不到音檔上傳欄位，請手動選取音檔');
    }
  }
}

// ── 完成，等待用戶操作 ────────────────────────────────────────────────────────
console.log('\n' + '='.repeat(50));
console.log('自動填入完成！請在瀏覽器中：');
console.log('  1. 確認標題與節目介紹正確');
console.log('  2. 設定封面圖（如需）');
console.log('  3. 設定上架時間');
console.log('  4. 點擊「發布」按鈕');
console.log('='.repeat(50));
console.log('\n發布完成後按 Ctrl+C 關閉瀏覽器。\n');

// 保持瀏覽器開啟
await new Promise(() => {});
