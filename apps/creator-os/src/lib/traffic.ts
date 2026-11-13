// 總流量第一階段的資料口徑（成析定義，見 docs/briefs/CREATOR-OS-TRAFFIC-2026-11/BRIEF.md）。
// Worker 與前端共用這份檔案，平台、觀察窗與 CSV 驗證只維護一處。

export const TRAFFIC_PLATFORMS = [
  "Firstory",
  "Spotify",
  "Apple Podcasts",
  "YouTube 正片",
  "YouTube Shorts",
  "FB",
  "IG",
  "Threads",
  "網站",
] as const;

export type TrafficPlatform = (typeof TRAFFIC_PLATFORMS)[number];

export const TRAFFIC_WINDOWS = ["D1", "D7", "D30"] as const;
export type TrafficWindow = (typeof TRAFFIC_WINDOWS)[number];

export const TRAFFIC_SOURCES = ["手填", "CSV"] as const;
export type TrafficSource = (typeof TRAFFIC_SOURCES)[number];

/** 各平台「主要數字」沿用平台後台原名；不同平台不得相加。 */
export const PRIMARY_METRIC_LABEL: Record<TrafficPlatform, string> = {
  Firstory: "收聽",
  Spotify: "串流",
  "Apple Podcasts": "收聽",
  "YouTube 正片": "觀看",
  "YouTube Shorts": "觀看",
  FB: "觀看",
  IG: "觀看",
  Threads: "瀏覽",
  網站: "瀏覽量",
};

export type TrafficInput = {
  episode: string;
  contentLabel: string;
  platform: TrafficPlatform;
  window: TrafficWindow;
  primaryValue: number | null;
  reach: number | null;
  engagements: number | null;
  linkClicks: number | null;
  followerDelta: number | null;
  note: string;
};

export type TrafficRow = Omit<TrafficInput, "primaryValue"> & {
  primaryValue: number;
  id: string;
  source: TrafficSource;
  enteredBy: string;
  updatedAt: string;
};

export const CSV_COLUMNS = [
  "episode",
  "content_label",
  "platform",
  "window",
  "primary_value",
  "reach",
  "engagements",
  "link_clicks",
  "follower_delta",
  "note",
] as const;

export const MAX_IMPORT_ROWS = 500;

const platformSet = new Set<string>(TRAFFIC_PLATFORMS);
const windowSet = new Set<string>(TRAFFIC_WINDOWS);

function parseCount(raw: unknown, field: string, allowNegative: boolean): { value: number | null; error?: string } {
  if (raw === null || raw === undefined) return { value: null };
  if (typeof raw === "number") {
    if (!Number.isInteger(raw)) return { value: null, error: `${field} 必須是整數` };
    if (!allowNegative && raw < 0) return { value: null, error: `${field} 不可為負數` };
    return { value: raw };
  }
  if (typeof raw !== "string") return { value: null, error: `${field} 格式錯誤` };
  const text = raw.trim().replace(/,/g, "");
  if (!text) return { value: null };
  if (!/^[+-]?\d+$/.test(text)) return { value: null, error: `${field} 必須是整數（收到「${raw}」）` };
  const value = Number(text);
  if (!Number.isSafeInteger(value)) return { value: null, error: `${field} 數字過大` };
  if (!allowNegative && value < 0) return { value: null, error: `${field} 不可為負數` };
  return { value };
}

/** 驗證一列輸入；手填 API 與 CSV 匯入共用。回傳錯誤清單，空陣列代表通過。 */
export function validateTrafficInput(raw: Record<string, unknown>): { input?: TrafficInput; errors: string[] } {
  const errors: string[] = [];
  const episode = typeof raw.episode === "string" ? raw.episode.trim().toUpperCase() : "";
  if (!episode) errors.push("episode 必填（例：S4EP3）");
  else if (episode.length > 40) errors.push("episode 超過 40 字");

  const contentLabel = typeof raw.contentLabel === "string" ? raw.contentLabel.trim() : "";
  if (contentLabel.length > 120) errors.push("content_label 超過 120 字");

  const platform = typeof raw.platform === "string" ? raw.platform.trim() : "";
  if (!platformSet.has(platform)) errors.push(`platform 必須是：${TRAFFIC_PLATFORMS.join("、")}`);

  const window = typeof raw.window === "string" ? raw.window.trim().toUpperCase() : "";
  if (!windowSet.has(window)) errors.push("window 必須是 D1、D7 或 D30");

  const primary = parseCount(raw.primaryValue, "primary_value", false);
  const reach = parseCount(raw.reach, "reach", false);
  const engagements = parseCount(raw.engagements, "engagements", false);
  const linkClicks = parseCount(raw.linkClicks, "link_clicks", false);
  const followerDelta = parseCount(raw.followerDelta, "follower_delta", true);
  for (const result of [primary, reach, engagements, linkClicks, followerDelta]) if (result.error) errors.push(result.error);
  if (primary.value === null && !primary.error) errors.push("primary_value 必填");

  const note = typeof raw.note === "string" ? raw.note.trim() : "";
  if (note.length > 500) errors.push("note 超過 500 字");

  if (errors.length) return { errors };
  return {
    errors,
    input: {
      episode,
      contentLabel,
      platform: platform as TrafficPlatform,
      window: window as TrafficWindow,
      primaryValue: primary.value,
      reach: reach.value,
      engagements: engagements.value,
      linkClicks: linkClicks.value,
      followerDelta: followerDelta.value,
      note,
    },
  };
}

/** 最小 CSV 解析：支援雙引號、引號內逗號與換行、CRLF、UTF-8 BOM。 */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;
  const source = text.replace(/^﻿/, "");
  for (let index = 0; index < source.length; index += 1) {
    const char = source[index];
    if (quoted) {
      if (char === '"') {
        if (source[index + 1] === '"') {
          field += '"';
          index += 1;
        } else quoted = false;
      } else field += char;
      continue;
    }
    if (char === '"') quoted = true;
    else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n" || char === "\r") {
      if (char === "\r" && source[index + 1] === "\n") index += 1;
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else field += char;
  }
  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }
  return rows.filter((cells) => cells.some((cell) => cell.trim().length));
}

export type CsvLineError = { line: number; messages: string[] };

/** 把 CSV 文字轉成待匯入的列；line 為 CSV 實際行號（表頭為第 1 行）。 */
export function csvToTrafficInputs(text: string): { inputs: TrafficInput[]; errors: CsvLineError[] } {
  const table = parseCsv(text);
  if (!table.length) return { inputs: [], errors: [{ line: 1, messages: ["檔案是空的"] }] };
  const header = table[0].map((cell) => cell.trim().toLowerCase());
  const missing = CSV_COLUMNS.filter((column) => !header.includes(column));
  if (missing.length) return { inputs: [], errors: [{ line: 1, messages: [`表頭缺少欄位：${missing.join(", ")}`] }] };
  const body = table.slice(1);
  if (body.length > MAX_IMPORT_ROWS) return { inputs: [], errors: [{ line: 1, messages: [`一次最多匯入 ${MAX_IMPORT_ROWS} 列，這份有 ${body.length} 列`] }] };

  const at = (cells: string[], column: (typeof CSV_COLUMNS)[number]) => cells[header.indexOf(column)] ?? "";
  const inputs: TrafficInput[] = [];
  const errors: CsvLineError[] = [];
  const seen = new Map<string, number>();
  body.forEach((cells, offset) => {
    const line = offset + 2;
    const { input, errors: messages } = validateTrafficInput({
      episode: at(cells, "episode"),
      contentLabel: at(cells, "content_label"),
      platform: at(cells, "platform"),
      window: at(cells, "window"),
      primaryValue: at(cells, "primary_value"),
      reach: at(cells, "reach"),
      engagements: at(cells, "engagements"),
      linkClicks: at(cells, "link_clicks"),
      followerDelta: at(cells, "follower_delta"),
      note: at(cells, "note"),
    });
    if (!input) {
      errors.push({ line, messages });
      return;
    }
    const key = trafficKey(input);
    const earlier = seen.get(key);
    if (earlier) {
      errors.push({ line, messages: [`與第 ${earlier} 行重複（同集數、內容、平台、觀察窗）`] });
      return;
    }
    seen.set(key, line);
    inputs.push(input);
  });
  return { inputs, errors };
}

export function trafficKey(input: Pick<TrafficInput, "episode" | "contentLabel" | "platform" | "window">) {
  return [input.episode, input.contentLabel, input.platform, input.window].join("\u0000");
}

/** 集數排序：S4EP10 排在 S4EP9 之後；無法解析的放最後。 */
export function compareEpisodes(a: string, b: string) {
  const parse = (value: string) => value.match(/^S(\d+)EP(\d+)$/i)?.slice(1).map(Number);
  const left = parse(a);
  const right = parse(b);
  if (left && right) return left[0] - right[0] || left[1] - right[1];
  if (left) return -1;
  if (right) return 1;
  return a.localeCompare(b);
}
