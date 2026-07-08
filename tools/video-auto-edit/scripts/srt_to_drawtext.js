// 把 SRT 轉成 FFmpeg drawtext filter chain
// 用法: node srt_to_drawtext.js input.srt fontfile output_filter.txt

const fs = require('fs');
const [,, srtPath, fontFile, outPath] = process.argv;

const raw = fs.readFileSync(srtPath, 'utf8').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
const blocks = raw.trim().split(/\n{2,}/);

function timeToSec(t) {
  const [hms, ms] = t.replace(',', '.').split('.');
  const [h, m, s] = hms.split(':').map(Number);
  return h * 3600 + m * 60 + s + parseFloat('0.' + ms);
}

function escapeText(s) {
  // FFmpeg drawtext escaping: ' : \ and special chars
  return s
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "’")   // curly apostrophe to avoid shell issues
    .replace(/:/g, '\\:')
    .replace(/\n/g, ' ');
}

const subtitles = blocks.map(b => {
  const lines = b.trim().split('\n');
  if (lines.length < 3) return null;
  const [start, end] = lines[1].split(' --> ');
  const text = lines.slice(2).join(' ');
  return { start: timeToSec(start), end: timeToSec(end), text };
}).filter(Boolean);

// Build chained drawtext
// Each subtitle: drawtext with enable='between(t,START,END)'
const esc_font = fontFile.replace(/:/g, '\\:').replace(/ /g, '\\ ');

let chain = '[comp]';
const filters = subtitles.map((s, i) => {
  const labelIn = i === 0 ? '[comp]' : `[sub${i-1}]`;
  const labelOut = i === subtitles.length - 1 ? '[with_subs]' : `[sub${i}]`;
  const escaped = escapeText(s.text);
  return (
    `${labelIn}drawtext=` +
    `fontfile='${esc_font}':` +
    `text='${escaped}':` +
    `fontcolor=white:fontsize=36:` +
    `x=(w-text_w)/2:y=h-120:` +
    `box=1:boxcolor=black@0.55:boxborderw=10:` +
    `enable='between(t,${s.start.toFixed(3)},${s.end.toFixed(3)})'` +
    `${labelOut}`
  );
});

const filterStr = filters.join(';\n');
fs.writeFileSync(outPath, filterStr, 'utf8');
console.log(`Written ${subtitles.length} subtitle drawtext filters to ${outPath}`);
