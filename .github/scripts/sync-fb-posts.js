const https = require('https');
const fs = require('fs');
const path = require('path');

const PAGE_ID = '711396992562275';
const IG_USER_ID = '17841479177621519';
const TOKEN = process.env.FB_PAGE_ACCESS_TOKEN;
const BLOG_DIR = path.join(process.cwd(), 'site', 'src', 'content', 'blog');

if (!TOKEN) {
  console.error('FB_PAGE_ACCESS_TOKEN is not set');
  process.exit(1);
}

function httpsGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

function httpsPost(urlStr, params) {
  return new Promise((resolve, reject) => {
    const qs = Object.entries(params)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      .join('&');
    const fullUrl = `${urlStr}?${qs}`;
    const url = new URL(fullUrl);
    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method: 'POST',
      headers: { 'Content-Length': 0 },
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

function slugify(postId) {
  const parts = postId.split('_');
  return `fb-${parts[parts.length - 1]}`;
}

function formatDate(isoString) {
  return isoString.substring(0, 10);
}

// 只有居易網誌的 FB 長文（含網站文章連結）才轉發到 IG。
// Reels、金句短片與週一主題文在 IG 已由星期天原生發布，轉發只會重複。
const BLOG_LINK_RE = /https?:\/\/beyond-ans\.com\/blog\/[^\s)）]+/;

function blogLinkOf(post) {
  const m = (post.message || '').match(BLOG_LINK_RE);
  return m ? m[0] : null;
}

function igCaption(post) {
  const link = blogLinkOf(post);
  if (post.message.length <= 2200 || !link) return post.message.substring(0, 2200);
  const tail = `\n\n全文：${link}`;
  const room = 2200 - tail.length;
  const cut = post.message.lastIndexOf('\n', room);
  return post.message.substring(0, cut > room * 0.7 ? cut : room).trim() + tail;
}

function postToMarkdown(post, igPostId) {
  if (!post.message) return null;

  const slug = slugify(post.id);
  const date = formatDate(post.created_time);
  const lines = post.message.split('\n').map(l => l.trim()).filter(Boolean);
  const firstLine = lines[0] || '';
  const title = firstLine.length > 60 ? firstLine.substring(0, 57) + '...' : firstLine;
  const desc = post.message.replace(/\n/g, ' ').trim().substring(0, 100);
  const body = lines.join('\n\n');

  const md = [
    '---',
    `title: "${title.replace(/"/g, '\\"')}"`,
    `date: "${date}"`,
    `description: "${desc.replace(/"/g, '\\"')}"`,
    ...(post.full_picture ? [`image: "${post.full_picture}"`] : []),
    `fbPostId: "${post.id}"`,
    ...(igPostId ? [`igPostId: "${igPostId}"`] : []),
    // 網站上已有原文：留檔記錄同步狀態，但不顯示成另一篇網誌
    ...(blogLinkOf(post) ? [`mirrorOf: "${blogLinkOf(post)}"`] : []),
    '---',
    '',
    body,
    '',
  ].join('\n');

  return { slug, filename: `${slug}.md`, markdown: md };
}

async function postToInstagram(post) {
  if (!post.full_picture) {
    console.log(`  IG skip (no image): ${post.id}`);
    return null;
  }
  if (!post.message) {
    console.log(`  IG skip (no caption): ${post.id}`);
    return null;
  }

  const caption = igCaption(post);

  // Step 1: Create media container
  const containerRes = await httpsPost(
    `https://graph.facebook.com/v25.0/${IG_USER_ID}/media`,
    { image_url: post.full_picture, caption, access_token: TOKEN }
  );

  if (containerRes.error) {
    console.error(`  IG container error: ${containerRes.error.message}`);
    return null;
  }

  const containerId = containerRes.id;
  console.log(`  IG container: ${containerId}`);

  await sleep(3000);

  // Step 2: Publish
  const publishRes = await httpsPost(
    `https://graph.facebook.com/v25.0/${IG_USER_ID}/media_publish`,
    { creation_id: containerId, access_token: TOKEN }
  );

  if (publishRes.error) {
    console.error(`  IG publish error: ${publishRes.error.message}`);
    return null;
  }

  console.log(`  IG published: ${publishRes.id}`);
  return publishRes.id;
}

function fileHasIgPostId(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8').includes('igPostId:');
  } catch {
    return false;
  }
}

function appendIgPostIdToFile(filePath, igPostId) {
  let content = fs.readFileSync(filePath, 'utf8');
  // Find closing --- of frontmatter (second occurrence)
  const secondDash = content.indexOf('\n---', 4);
  if (secondDash !== -1) {
    content = content.slice(0, secondDash) + `\nigPostId: "${igPostId}"` + content.slice(secondDash);
    fs.writeFileSync(filePath, content, 'utf8');
  }
}

async function main() {
  const url = `https://graph.facebook.com/v25.0/${PAGE_ID}/posts?fields=id,message,created_time,full_picture&limit=10&access_token=${encodeURIComponent(TOKEN)}`;

  console.log(`Fetching posts from page ${PAGE_ID}...`);
  const data = await httpsGet(url);

  if (data.error) {
    console.error('Facebook API error:', data.error.message);
    process.exit(1);
  }

  const posts = data.data || [];
  console.log(`Found ${posts.length} posts`);

  let newBlogCount = 0;
  let newIgCount = 0;

  for (const post of posts) {
    if (!post.message) continue;

    const mirrorToIg = Boolean(blogLinkOf(post));

    const slug = slugify(post.id);
    const filename = `${slug}.md`;
    const filePath = path.join(BLOG_DIR, filename);
    const exists = fs.existsSync(filePath);

    console.log(`\nProcessing: ${filename}`);

    if (!exists) {
      // New post: create blog file; only blog-article posts go to IG
      const igPostId = mirrorToIg ? await postToInstagram(post) : null;
      if (igPostId) newIgCount++;

      const result = postToMarkdown(post, igPostId);
      if (!result) continue;
      fs.writeFileSync(filePath, result.markdown, 'utf8');
      console.log(`  Blog created: ${filename}`);
      newBlogCount++;
    } else if (mirrorToIg && !fileHasIgPostId(filePath)) {
      // Existing blog file not yet on IG: catch-up sync
      const igPostId = await postToInstagram(post);
      if (igPostId) {
        appendIgPostIdToFile(filePath, igPostId);
        console.log(`  IG catch-up synced: ${filename}`);
        newIgCount++;
      }
      // Add delay between IG posts to respect rate limits
      await sleep(2000);
    } else {
      console.log(`  Skip (already synced)`);
    }
  }

  console.log(`\nDone. Blog: ${newBlogCount} new, IG: ${newIgCount} new.`);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
