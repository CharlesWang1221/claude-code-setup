import type { ContentItem, Task } from "@/lib/content-workflow";

const configuredApiUrl = process.env.NEXT_PUBLIC_CREATOR_OS_API_URL?.replace(/\/$/, "");

type CloudState = { content: ContentItem[]; tasks: Task[] };

function endpoint(path: string) {
  // 部署在 Worker 後，介面與 API 同網域，避免跨網域 Cookie／CORS 造成協作者登入失敗。
  if (typeof window !== "undefined" && window.location.hostname.endsWith(".workers.dev")) return path;
  if (!configuredApiUrl) throw new Error("尚未設定 NEXT_PUBLIC_CREATOR_OS_API_URL。");
  return `${configuredApiUrl}${path}`;
}

async function request<T>(path: string, init?: RequestInit) {
  const response = await fetch(endpoint(path), {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
    credentials: "include",
  });
  const body = await response.json().catch(() => ({})) as T & { error?: string };
  if (!response.ok) throw new Error(body.error ?? "雲端同步失敗。");
  return body;
}

export function isCloudSyncConfigured() {
  return (typeof window !== "undefined" && window.location.hostname.endsWith(".workers.dev")) || Boolean(configuredApiUrl);
}

export function loadCloudState() {
  return request<CloudState>("/v1/state");
}

export function importLocalState(state: CloudState) {
  return request<{ ok: true; imported: { content: number; tasks: number } }>("/v1/import", {
    method: "POST",
    body: JSON.stringify(state),
  });
}

export function saveCloudState(state: CloudState) {
  return request<{ ok: true; savedAt: string }>("/v1/state", {
    method: "POST",
    body: JSON.stringify(state),
  });
}

export function createCloudBackup() {
  return request<{ ok: true; backup: { fileName: string; exportedAt: string } }>("/v1/backups", { method: "POST" });
}
