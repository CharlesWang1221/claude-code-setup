/**
 * 《不標準答案》YouTube 自動上傳工具
 *
 * 用法：
 *   node tools/youtube-upload.js --episode ep-s2ep7
 *
 * 第一次執行會打開瀏覽器要求 Google 授權，之後 token 會快取在 tools/youtube-token.json
 *
 * 前置需求：
 *   1. tools/client_secret.json（從 Google Cloud Console 下載）
 *   2. node_modules/googleapis（已安裝）
 */

const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const SCOPES = ['https://www.googleapis.com/auth/youtube.upload'];
const TOKEN_PATH  = path.join(__dirname, 'youtube-token.json');
const CREDS_PATH  = path.join(__dirname, 'client_secret.json');
const OUTPUT_ROOT = path.join(__dirname, '..', 'output');

// ── 取得 episode 參數 ──────────────────────────────────────────
const epArg = process.argv.indexOf('--episode');
if (epArg === -1 || !process.argv[epArg + 1]) {
  console.error('用法：node tools/youtube-upload.js --episode <資料夾名稱>');
  console.error('範例：node tools/youtube-upload.js --episode ep-s2ep7');
  process.exit(1);
}
const episodeDir = path.join(OUTPUT_ROOT, process.argv[epArg + 1]);

// ── 讀取 youtube.txt，解析標題與說明 ─────────────────────────
function parseYoutubeMeta(dir) {
  const txt = fs.readFileSync(path.join(dir, 'youtube.txt'), 'utf8');

  const titleMatch = txt.match(/【YouTube 標題】\s*\n([^\n]+)/);
  const title = titleMatch ? titleMatch[1].trim() : '（請填入標題）';

  const descStart = txt.indexOf('【YouTube 說明欄 Description】');
  const descEnd   = txt.indexOf('\n---\n', descStart + 1);
  const description = descStart !== -1
    ? txt.slice(descStart + '【YouTube 說明欄 Description】'.length, descEnd !== -1 ? descEnd : undefined).trim()
    : '';

  const tagMatch = txt.match(/^#(.+)$/m);
  const tags = tagMatch
    ? tagMatch[1].split(/\s+#/).map(t => t.replace(/^#/, '').trim()).filter(Boolean)
    : [];

  return { title, description, tags };
}

// ── 找影片檔（第一個 .mp4）─────────────────────────────────────
function findVideo(dir) {
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.mp4'));
  if (!files.length) throw new Error(`${dir} 裡找不到 .mp4 影片檔`);
  return path.join(dir, files[0]);
}

// ── OAuth 授權 ────────────────────────────────────────────────
async function authenticate() {
  if (!fs.existsSync(CREDS_PATH)) {
    console.error(`\n找不到 ${CREDS_PATH}`);
    console.error('請先完成 Google Cloud Console 設定（見下方說明）');
    process.exit(1);
  }

  const creds = JSON.parse(fs.readFileSync(CREDS_PATH));
  const { client_secret, client_id, redirect_uris } = creds.installed || creds.web;
  const oauth2 = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);

  if (fs.existsSync(TOKEN_PATH)) {
    oauth2.setCredentials(JSON.parse(fs.readFileSync(TOKEN_PATH)));
    return oauth2;
  }

  // 支援 --code 參數直接交換 token
  const codeArgIdx = process.argv.indexOf('--code');
  let code;
  if (codeArgIdx !== -1 && process.argv[codeArgIdx + 1]) {
    code = process.argv[codeArgIdx + 1].trim();
  } else {
    const authUrl = oauth2.generateAuthUrl({ access_type: 'offline', scope: SCOPES });
    console.log('\n請在瀏覽器開啟以下連結，用 another20251021@gmail.com 登入並授權：\n');
    console.log(authUrl);
    console.log('');
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    code = await new Promise(r => rl.question('授權完成後，把網址列的 code= 後面那段貼上來：', r));
    rl.close();
    code = code.trim();
  }

  const { tokens } = await oauth2.getToken(code);
  oauth2.setCredentials(tokens);
  fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens, null, 2));
  console.log('Token 已儲存，下次不需要再重新授權。\n');
  return oauth2;
}

// ── 上傳影片 ──────────────────────────────────────────────────
async function upload(auth, videoPath, meta) {
  const youtube  = google.youtube({ version: 'v3', auth });
  const fileSize = fs.statSync(videoPath).size;

  console.log(`\n開始上傳：${path.basename(videoPath)}`);
  console.log(`標題：${meta.title}\n`);

  const res = await youtube.videos.insert(
    {
      part: ['snippet', 'status'],
      requestBody: {
        snippet: {
          title: meta.title,
          description: meta.description,
          tags: meta.tags,
          categoryId: '22',         // People & Blogs
          defaultLanguage: 'zh-TW',
        },
        status: { privacyStatus: 'private' }, // 先上傳為私人，確認後再改公開
      },
      media: { body: fs.createReadStream(videoPath) },
    },
    {
      onUploadProgress: evt => {
        const pct = ((evt.bytesRead / fileSize) * 100).toFixed(1);
        process.stdout.write(`\r上傳進度：${pct}%   `);
      },
    }
  );

  console.log(`\n\n上傳完成！`);
  console.log(`影片 ID：${res.data.id}`);
  console.log(`YouTube Studio：https://studio.youtube.com/video/${res.data.id}/edit`);
  return res.data;
}

// ── 主流程 ────────────────────────────────────────────────────
(async () => {
  try {
    const meta      = parseYoutubeMeta(episodeDir);
    const videoPath = findVideo(episodeDir);
    const auth      = await authenticate();
    await upload(auth, videoPath, meta);
  } catch (err) {
    console.error('\n錯誤：', err.message);
    process.exit(1);
  }
})();
