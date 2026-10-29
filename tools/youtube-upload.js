/**
 * 《不標準答案》YouTube 自動上傳工具
 *
 * 用法：
 *   node tools/youtube-upload.js --episode ep-s2ep7
 *   node tools/youtube-upload.js --episode ep-s2ep7 --update <videoId>
 *   node tools/youtube-upload.js --update <videoId> --thumbnail-only --thumbnail <封面>
 *   node tools/youtube-upload.js --episode ep-s2ep7 --publish-at 2026-10-20T07:00:00+08:00
 *
 *   node tools/youtube-upload.js --video output/ep-s3ep11/s3ep11-teaser-v3.mp4 \
 *     --meta <youtube.txt> --thumbnail <封面> --publish-at 2026-10-20T20:30:00+08:00
 *
 * --publish-at：上傳時直接設定 YouTube 預約公開時間（須含 +08:00 時區且晚於現在），
 * 影片保持私人直到該時間自動公開；--public-now 則立即公開；兩者皆未加時只上傳為私人。
 * AI 標示：預設送出 containsSyntheticMedia=false（「變造或合成內容」選否）；
 * 只有 AI 複製聲音或擬真 AI 人物／場景才加 --synthetic-media 改為 true。
 * --video／--meta／--thumbnail／--qa-report：直接指定檔案（週計畫 Shorts 用），
 * 不再從 --episode 資料夾自動尋找；--video 存在時可省略 --episode。
 *
 * 上傳新影片前會先通過鐵雄稽核閘門（tools/qa-gate/qa-gate.cjs）：需有 PASS 報告且雜湊一致。
 * 報告位置可在 .publish-status.json 以 qa_report 指定；只更新說明欄（--update）不經閘門。
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
const { assertQaPass } = require('./qa-gate/qa-gate.cjs');

const SCOPES = ['https://www.googleapis.com/auth/youtube.upload'];
const TOKEN_PATH  = path.join(__dirname, 'youtube-token.json');
const CREDS_PATH  = path.join(__dirname, 'client_secret.json');
const OUTPUT_ROOT = path.join(__dirname, '..', 'output');
const PROJECT_ROOT = path.join(__dirname, '..');

// ── 取得 episode 參數 ──────────────────────────────────────────
function argValue(name) {
  const i = process.argv.indexOf(name);
  if (i === -1) return null;
  const v = process.argv[i + 1];
  if (!v || v.startsWith('--')) throw new Error(`${name} 後面需要值`);
  return v;
}

function explicitFile(name) {
  const v = argValue(name);
  if (!v) return null;
  const p = path.resolve(PROJECT_ROOT, v);
  if (!fs.existsSync(p)) throw new Error(`${name} 指定的檔案不存在：${v}`);
  return p;
}

const epArg = process.argv.indexOf('--episode');
const hasVideoArg = process.argv.includes('--video');
const hasUpdateArg = process.argv.includes('--update');
if ((epArg === -1 || !process.argv[epArg + 1]) && !hasVideoArg && !hasUpdateArg) {
  console.error('用法：node tools/youtube-upload.js --episode <資料夾名稱>');
  console.error('　或：node tools/youtube-upload.js --video <mp4> --meta <youtube.txt> [--thumbnail <圖>] [--publish-at <時間>]');
  console.error('範例：node tools/youtube-upload.js --episode ep-s2ep7');
  process.exit(1);
}
const episodeDir = epArg !== -1 ? path.join(OUTPUT_ROOT, process.argv[epArg + 1]) : null;

// ── 讀取 youtube.txt，解析標題與說明 ─────────────────────────
function parseYoutubeMeta(dir, metaPath) {
  const txt = fs.readFileSync(metaPath || path.join(dir, 'youtube.txt'), 'utf8');

  const titleMatch = txt.match(/【YouTube 標題】\s*\n([^\n]+)/)
    || txt.match(/^標題[：:]\s*(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : '（請填入標題）';

  const descStart = txt.indexOf('【YouTube 說明欄 Description】');
  // 說明欄到下一個 --- 或下一個【區塊】為止，避免把【YouTube 標籤】吃進說明
  const descEnds = ['\n---\n', '\n【']
    .map(sep => txt.indexOf(sep, descStart + 1))
    .filter(i => i !== -1);
  const descEnd = descEnds.length ? Math.min(...descEnds) : -1;
  let description = descStart !== -1
    ? txt.slice(descStart + '【YouTube 說明欄 Description】'.length, descEnd !== -1 ? descEnd : undefined).trim()
    : '';
  if (!description) {
    const simpleDescription = txt.match(/^說明[：:]\s*\n([\s\S]*)$/m);
    description = simpleDescription ? simpleDescription[1].trim() : '';
  }

  // 優先讀【YouTube 標籤】（逗號分隔）；沒有才退回說明欄第一行 hashtag
  const tagBlock = txt.match(/【YouTube 標籤】\s*\n([^\n]+)/);
  const tagMatch = txt.match(/^#(.+)$/m);
  const tags = tagBlock
    ? tagBlock[1].split(/[,，、]/).map(t => t.replace(/^#/, '').trim()).filter(Boolean)
    : tagMatch
      ? tagMatch[1].split(/\s+#/).map(t => t.replace(/^#/, '').trim()).filter(Boolean)
      : [];

  return { title, description, tags };
}

// ── 更新既有影片 metadata，不重傳影片 ───────────────────────
async function updateMetadata(auth, videoId, meta, thumbnailPath = null) {
  const youtube = google.youtube({ version: 'v3', auth });
  await youtube.videos.update({
    part: ['snippet'],
    requestBody: {
      id: videoId,
      snippet: {
        title: meta.title,
        description: meta.description,
        tags: meta.tags,
        categoryId: '22',
        defaultLanguage: 'zh-TW',
      },
    },
  });

  if (thumbnailPath) {
    await setThumbnail(auth, videoId, thumbnailPath);
  }

  console.log('\n影片資料已更新！');
  console.log(`影片 ID：${videoId}`);
  console.log(`YouTube Studio：https://studio.youtube.com/video/${videoId}/edit`);
}

async function setThumbnail(auth, videoId, thumbnailPath) {
  const youtube = google.youtube({ version: 'v3', auth });
  const thumbnailResult = await youtube.thumbnails.set({
    videoId,
    media: { body: fs.createReadStream(thumbnailPath) },
  });
  const returnedThumbnail = thumbnailResult.data?.items?.[0]?.default?.url
    || thumbnailResult.data?.items?.[0]?.high?.url
    || null;
  console.log(`縮圖已套用：${path.basename(thumbnailPath)}`);
  console.log(`API 回傳縮圖：${returnedThumbnail || '無 URL'}`);
  console.log(`仍須到 Studio 重新載入讀回：https://studio.youtube.com/video/${videoId}/edit`);
}

// ── 找正式影片與縮圖 ───────────────────────────────────────────
function readPublishStatus(dir) {
  if (!dir) return null;
  const statusPath = path.join(dir, '.publish-status.json');
  if (!fs.existsSync(statusPath)) return null;
  return JSON.parse(fs.readFileSync(statusPath, 'utf8'));
}

function findVideo(dir) {
  const status = readPublishStatus(dir);
  const declared = status?.youtube_assets?.render_file;
  if (declared) {
    const declaredPath = path.resolve(PROJECT_ROOT, declared);
    if (!fs.existsSync(declaredPath)) {
      throw new Error(`狀態檔指定的正式影片不存在：${declared}`);
    }
    return declaredPath;
  }

  const rootFiles = fs.readdirSync(dir).filter(f => f.endsWith('.mp4')).map(f => path.join(dir, f));
  const youtubeDir = path.join(dir, 'youtube');
  const youtubeFiles = fs.existsSync(youtubeDir)
    ? fs.readdirSync(youtubeDir).filter(f => f.endsWith('.mp4')).map(f => path.join(youtubeDir, f))
    : [];
  const candidates = [...rootFiles, ...youtubeFiles];
  if (!candidates.length) throw new Error(`${dir} 裡找不到 .mp4 影片檔`);
  if (candidates.length > 1) {
    throw new Error(
      `找到多個影片候選，為避免誤上傳請在 .publish-status.json 指定 youtube_assets.render_file：\n${candidates.map(f => `- ${path.relative(PROJECT_ROOT, f)}`).join('\n')}`
    );
  }
  return candidates[0];
}

function findThumbnail(dir) {
  const status = readPublishStatus(dir);
  const declared = status?.inputs?.thumbnail;
  if (declared) {
    const declaredPath = path.resolve(PROJECT_ROOT, declared);
    if (!fs.existsSync(declaredPath)) {
      throw new Error(`狀態檔指定的縮圖不存在：${declared}`);
    }
    return declaredPath;
  }

  const youtubeDir = path.join(dir, 'youtube');
  if (!fs.existsSync(youtubeDir)) return null;
  const files = fs.readdirSync(youtubeDir)
    .filter(f => /^youtube-thumbnail-.+\.(jpg|jpeg|png)$/i.test(f))
    .sort();
  return files.length ? path.join(youtubeDir, files[files.length - 1]) : null;
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
// ── 預約公開時間 ──────────────────────────────────────────────
function parsePublishAt() {
  if (process.argv.includes('--public-now') && process.argv.includes('--publish-at')) {
    throw new Error('--public-now 與 --publish-at 不可同時使用');
  }
  const i = process.argv.indexOf('--publish-at');
  if (i === -1) return null;
  const raw = process.argv[i + 1];
  if (!raw || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?\+08:00$/.test(raw)) {
    throw new Error('--publish-at 需為含 +08:00 的完整時間，例如 2026-10-20T07:00:00+08:00');
  }
  const at = new Date(raw);
  if (Number.isNaN(at.getTime()) || at.getTime() <= Date.now() + 15 * 60 * 1000) {
    throw new Error(`--publish-at ${raw} 已過或距現在不足 15 分鐘，停止上傳`);
  }
  return at;
}

async function upload(auth, videoPath, thumbnailPath, meta, publishAt) {
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
        // 預約片先私人；明確 --public-now 才立即公開。
        status: {
          privacyStatus: process.argv.includes('--public-now') ? 'public' : 'private',
          containsSyntheticMedia: process.argv.includes('--synthetic-media'),
          ...(publishAt ? { publishAt: publishAt.toISOString() } : {}),
        },
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

  if (publishAt) {
    const got = res.data.status?.publishAt;
    if (!got || new Date(got).getTime() !== publishAt.getTime()) {
      throw new Error(`影片 ${res.data.id} 已上傳為私人，但平台回傳的預約時間為 ${got || '無'}，與指定時間不符；不要重傳，改到 Studio 核對`);
    }
    console.log(`預約公開：${publishAt.toLocaleString('zh-TW', { timeZone: 'Asia/Taipei' })}（平台回傳 ${got}）`);
  } else if (process.argv.includes('--public-now')) {
    const got = res.data.status?.privacyStatus;
    if (got !== 'public') {
      throw new Error(`影片 ${res.data.id} 已上傳，但平台回傳隱私狀態為 ${got || '無'}，不是 public；不要重傳，改到 Studio 核對`);
    }
    console.log('立即公開：平台回傳 public');
  }

  if (thumbnailPath) {
    await youtube.thumbnails.set({
      videoId: res.data.id,
      media: { body: fs.createReadStream(thumbnailPath) },
    });
    console.log(`縮圖已套用：${path.basename(thumbnailPath)}`);
  } else {
    console.log('未找到縮圖，影片保留 YouTube 自動縮圖。');
  }

  console.log(`YouTube Studio：https://studio.youtube.com/video/${res.data.id}/edit`);
  return res.data;
}

// ── 主流程 ────────────────────────────────────────────────────
(async () => {
  try {
    const updateArg = process.argv.indexOf('--update');
    const videoId = updateArg !== -1 ? process.argv[updateArg + 1] : null;
    const thumbnailOnly = process.argv.includes('--thumbnail-only');

    if (updateArg !== -1 && !videoId) {
      throw new Error('--update 後面需要影片 ID');
    }
    if (thumbnailOnly) {
      if (!videoId) throw new Error('--thumbnail-only 必須搭配 --update <影片 ID>');
      const thumbnailPath = explicitFile('--thumbnail');
      if (!thumbnailPath) throw new Error('--thumbnail-only 必須指定 --thumbnail <封面>');
      const auth = await authenticate();
      await setThumbnail(auth, videoId, thumbnailPath);
      return;
    }

    const metaPath = explicitFile('--meta');
    if (!episodeDir && !metaPath) throw new Error('未指定 --episode 時必須提供 --meta');
    const meta = parseYoutubeMeta(episodeDir, metaPath);
    const publishAt = parsePublishAt();
    const auth = await authenticate();

    if (videoId) {
      const thumbnailPath = explicitFile('--thumbnail') || (episodeDir ? findThumbnail(episodeDir) : null);
      await updateMetadata(auth, videoId, meta, thumbnailPath);
    } else {
      const videoPath = explicitFile('--video') || findVideo(episodeDir);
      const status = readPublishStatus(episodeDir);
      const qaReport = explicitFile('--qa-report');
      assertQaPass(videoPath, { report: qaReport || status?.qa_report || status?.youtube_assets?.qa_report });
      const thumbnailPath = explicitFile('--thumbnail') || (episodeDir ? findThumbnail(episodeDir) : null);
      await upload(auth, videoPath, thumbnailPath, meta, publishAt);
    }
  } catch (err) {
    console.error('\n錯誤：', err.message);
    process.exit(1);
  }
})();
