const fs = require('fs');
const path = require('path');
const token = process.env.FB_PAGE_ACCESS_TOKEN;
if (!token) throw new Error('FB_PAGE_ACCESS_TOKEN is required');
const root = process.cwd();
const blog = path.join(root, 'site/src/content/blog');
const images = path.join(root, 'site/public/images/blog/facebook');
fs.mkdirSync(images, { recursive: true });
const getField = (s, k) => s.match(new RegExp('^' + k + ':\\s*"([^"]*)"', 'm'))?.[1];
function setField(s, key, value) {
  const line = key + ': "' + value + '"';
  const re = new RegExp('^' + key + ':.*$', 'm');
  return re.test(s) ? s.replace(re, line) : s.replace(/^---\r?\n/, match => match + line + '\n');
}
async function run() {
  let saved = 0, video = 0, unresolved = 0;
  for (const name of fs.readdirSync(blog).filter(n => n.endsWith('.md'))) {
    const file = path.join(blog, name);
    let text = fs.readFileSync(file, 'utf8');
    const id = getField(text, 'fbPostId');
    if (!id) continue;
    if (getField(text, 'sourceKind') === 'video') continue;
    const image = getField(text, 'image') || '';
    if (getField(text, 'sourceKind') === 'photo' && image.startsWith('/images/blog/facebook/') && fs.existsSync(path.join(root, 'site/public', image))) continue;
    try {
      const url = new URL('https://graph.facebook.com/v25.0/' + encodeURIComponent(id));
      url.searchParams.set('fields', 'id,full_picture,attachments{type,media_type}');
      url.searchParams.set('access_token', token);
      const res = await fetch(url, { signal: AbortSignal.timeout(20000) });
      const data = await res.json();
      if (!res.ok || data.error) throw new Error('Graph API request failed');
      const attachments = data.attachments?.data || [];
      const kinds = attachments.map(a => String(a.media_type || a.type || '').toLowerCase());
      if (kinds.some(k => k.includes('video') || k.includes('reel'))) {
        text = setField(text, 'sourceKind', 'video');
        fs.writeFileSync(file, text); video++; continue;
      }
      if (!kinds.length || !kinds.every(k => k.includes('photo') || k.includes('album'))) throw new Error('Unrecognised attachment type');
      if (!data.full_picture) throw new Error('No picture');
      const img = await fetch(data.full_picture, { signal: AbortSignal.timeout(20000) });
      const type = img.headers.get('content-type')?.split(';')[0].trim();
      const ext = ({'image/jpeg':'jpg','image/png':'png','image/webp':'webp'})[type];
      if (!img.ok || !ext) throw new Error('Invalid image response');
      const bytes = Buffer.from(await img.arrayBuffer());
      if (bytes.length < 1000 || bytes.length > 15000000) throw new Error('Invalid image size');
      const filename = name.replace(/\.md$/, '') + '.' + ext;
      fs.writeFileSync(path.join(images, filename), bytes);
      text = setField(text, 'sourceKind', 'photo');
      text = setField(text, 'image', '/images/blog/facebook/' + filename);
      fs.writeFileSync(file, text); saved++;
    } catch (err) {
      console.error(name + ': ' + err.message);
      unresolved++;
    }
  }
  console.log(JSON.stringify({ saved, video, unresolved }));
}
run().catch(err => { console.error(err.message); process.exitCode = 1; });
