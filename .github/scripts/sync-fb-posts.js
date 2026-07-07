const https = require('https');
const fs = require('fs');
const path = require('path');

const PAGE_ID = '711396992562275';
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

function slugify(postId) {
  const parts = postId.split('_');
  return `fb-${parts[parts.length - 1]}`;
}

function formatDate(isoString) {
  return isoString.substring(0, 10);
}

function postToMarkdown(post) {
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
    '---',
    '',
    body,
    '',
  ].join('\n');

  return { slug, filename: `${slug}.md`, markdown: md };
}

async function main() {
  const url = `https://graph.facebook.com/v25.0/${PAGE_ID}/posts?fields=id,message,created_time,full_picture&limit=10&access_token=${encodeURIComponent(TOKEN)}`;

  console.log(`Fetching posts from ${PAGE_ID}...`);
  const data = await httpsGet(url);

  if (data.error) {
    console.error('Facebook API error:', data.error.message);
    process.exit(1);
  }

  const posts = data.data || [];
  console.log(`Found ${posts.length} posts`);

  let newCount = 0;
  for (const post of posts) {
    const result = postToMarkdown(post);
    if (!result) continue;

    const filePath = path.join(BLOG_DIR, result.filename);
    if (fs.existsSync(filePath)) {
      console.log(`Skip (exists): ${result.filename}`);
      continue;
    }

    fs.writeFileSync(filePath, result.markdown, 'utf8');
    console.log(`Created: ${result.filename}`);
    newCount++;
  }

  console.log(`Done. ${newCount} new post(s) created.`);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
