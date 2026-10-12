const { google } = require('googleapis');
const fs = require('fs');
const creds = JSON.parse(fs.readFileSync('tools/client_secret.json'));
const c = creds.installed || creds.web;
const auth = new google.auth.OAuth2(c.client_id, c.client_secret, c.redirect_uris[0]);
auth.setCredentials(JSON.parse(fs.readFileSync('tools/youtube-token.json')));
(async () => {
  const y = google.youtube({ version: 'v3', auth });
  const r = await y.channels.list({ part: ['snippet', 'contentDetails'], mine: true });
  console.log(JSON.stringify(r.data.items.map(x => ({ id: x.id, title: x.snippet.title, uploads: x.contentDetails.relatedPlaylists.uploads })), null, 2));
})().catch(err => { console.error(err.response?.data || err.message); process.exit(1); });
