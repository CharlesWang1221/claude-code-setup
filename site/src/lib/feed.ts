import { XMLParser } from 'fast-xml-parser';

const RSS_URL = 'https://feed.firstory.me/rss/user/cmi76pcj000h7010chgezh8bs';

function cleanTitle(raw: string): string {
  // 1. 移除所有 emoji
  let t = raw.replace(/[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu, '');
  // 1b. 移除 variation selectors U+FE0E/FE0F 和零寬字符 U+200B–200D U+FEFF
  t = t.replace(/[︎️​‌‍﻿]/g, '');

  // 2. 取全形 ｜ 後面的部分（節目名稱前綴）
  const pipeIdx = t.lastIndexOf('｜');
  if (pipeIdx !== -1) t = t.slice(pipeIdx + 1);

  // 3. 移除開頭的欄目標籤（可能被《包住，先做一次）
  const stripLabels = (s: string) => s
    .replace(/^\s*【聊哉】\s*/u, '')
    .replace(/^\s*《聊哉》\s*/u, '')
    .replace(/^\s*《書喔〜吾聊へ》[：:]?\s*/u, '');
  t = stripLabels(t);

  // 4. 移除開頭殘留的書名號，再補一次欄目標籤（《🎙️【聊哉】 的情況）
  t = t.replace(/^\s*[《「]/u, '');
  t = stripLabels(t);

  // 5. 移除結尾集數標記（S2_EP.08、S1_EP.12、S2_EP2、.S2_EP.01）
  t = t.replace(/[\s._]*S?\d+[_.]?EP\.?\s*\d*\s*$/i, '');

  return t.replace(/\s+/g, ' ').trim();
}

export interface Episode {
  slug: string;
  title: string;
  pubDate: string;
  pubDateFormatted: string;
  duration: string;
  durationSeconds: number;
  description: string;
  audioUrl: string;
  season: number;
  episode: number;
  episodeLabel: string;
  link: string;
  image?: string;
}

export interface PodcastMeta {
  title: string;
  description: string;
  image: string;
  link: string;
}

function formatDuration(raw: string | number): string {
  if (typeof raw === 'number') {
    const h = Math.floor(raw / 3600);
    const m = Math.floor((raw % 3600) / 60);
    const s = raw % 60;
    if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    return `${m}'${String(s).padStart(2, '0')}"`;
  }
  // already formatted like "43:27"
  const parts = String(raw).split(':').map(Number);
  if (parts.length === 2) return `${parts[0]}'${String(parts[1]).padStart(2, '0')}"`;
  if (parts.length === 3) return `${parts[0]}:${String(parts[1]).padStart(2, '0')}:${String(parts[2]).padStart(2, '0')}`;
  return String(raw);
}

function toSeconds(raw: string | number): number {
  if (typeof raw === 'number') return raw;
  const parts = String(raw).split(':').map(Number);
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  return 0;
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: 'Asia/Taipei',
  });
}

function slugFromGuid(guid: string): string {
  // https://open.firstory.me/story/cmxxx → cmxxx
  const id = guid.split('/').pop() ?? guid;
  return id.replace(/[^a-z0-9-]/gi, '-').toLowerCase();
}

let _cache: { episodes: Episode[]; meta: PodcastMeta } | null = null;

export async function getFeed(): Promise<{ episodes: Episode[]; meta: PodcastMeta }> {
  if (_cache) return _cache;

  const res = await fetch(RSS_URL);
  if (!res.ok) throw new Error(`RSS fetch failed: ${res.status}`);
  const xml = await res.text();

  const parser = new XMLParser({
    ignoreAttributes: false,
    attributeNamePrefix: '@_',
    isArray: (name) => name === 'item',
  });
  const data = parser.parse(xml);
  const channel = data.rss.channel;

  const meta: PodcastMeta = {
    title: channel.title ?? '不標準答案',
    description: channel.description ?? '',
    image: channel['itunes:image']?.['@_href'] ?? channel.image?.url ?? '',
    link: channel.link ?? '',
  };

  const items: any[] = Array.isArray(channel.item) ? channel.item : [channel.item];

  const episodes: Episode[] = items
    .filter(Boolean)
    .map((item: any) => {
      const guid = item.guid?.['#text'] ?? item.guid ?? item.link ?? '';
      const rawDur = item['itunes:duration'] ?? 0;
      const season = Number(item['itunes:season'] ?? 1);
      const ep = Number(item['itunes:episode'] ?? 0);
      const episodeLabel = `S${season}·EP.${String(ep).padStart(2, '0')}`;

      return {
        slug: slugFromGuid(typeof guid === 'object' ? guid['#text'] ?? '' : String(guid)),
        title: cleanTitle(item.title ?? ''),
        pubDate: item.pubDate ?? '',
        pubDateFormatted: item.pubDate ? formatDate(item.pubDate) : '',
        duration: formatDuration(rawDur),
        durationSeconds: toSeconds(rawDur),
        description: item.description ?? item['itunes:summary'] ?? '',
        audioUrl: item.enclosure?.['@_url'] ?? '',
        season,
        episode: ep,
        episodeLabel,
        link: item.link ?? '',
        image: item['itunes:image']?.['@_href'],
      };
    })
    .sort((a, b) => new Date(b.pubDate).getTime() - new Date(a.pubDate).getTime());

  _cache = { episodes, meta };
  return _cache;
}
