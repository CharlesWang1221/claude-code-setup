import type { CsvLineError, TrafficInput, TrafficRow } from "@/lib/traffic";

// 與 creator-os-api.ts 相同的網域判斷；獨立一份，避免總流量頁依賴尚未同步的工作站主頁程式。
const configuredApiUrl = process.env.NEXT_PUBLIC_CREATOR_OS_API_URL?.replace(/\/$/, "");

function endpoint(path: string) {
  if (typeof window !== "undefined" && window.location.hostname.endsWith(".workers.dev")) return path;
  if (!configuredApiUrl) throw new Error("尚未設定 NEXT_PUBLIC_CREATOR_OS_API_URL，本機無法讀取雲端成效資料。");
  return `${configuredApiUrl}${path}`;
}

async function request<T>(path: string, init?: RequestInit) {
  const response = await fetch(endpoint(path), {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
    credentials: "include",
  });
  const body = await response.json().catch(() => ({})) as T & { error?: string };
  if (!response.ok) throw Object.assign(new Error(body.error ?? "雲端讀寫失敗。"), { body });
  return body;
}

export type TrafficRole = "owner" | "editor" | "viewer";

export type ImportSummary = {
  rows: TrafficInput[];
  errors: CsvLineError[];
  total: number;
  overwrites: number;
  inserts: number;
  maxRows: number;
};

export function loadTraffic() {
  return request<{ rows: TrafficRow[]; role: TrafficRole }>("/v1/traffic");
}

export function saveTraffic(input: Record<string, unknown>) {
  return request<{ ok: true; rows: TrafficRow[] }>("/v1/traffic", { method: "POST", body: JSON.stringify(input) });
}

export function previewTrafficCsv(csv: string) {
  return request<{ ok: true } & ImportSummary>("/v1/traffic/import", { method: "POST", body: JSON.stringify({ csv, mode: "preview" }) });
}

export function commitTrafficCsv(csv: string) {
  return request<{ ok: true; imported: number; overwrites: number; rows: TrafficRow[] }>("/v1/traffic/import", { method: "POST", body: JSON.stringify({ csv, mode: "commit" }) });
}
