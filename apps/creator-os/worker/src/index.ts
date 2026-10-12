type Role = "owner" | "editor" | "viewer";

type D1Result<T> = { results?: T[] };
type D1Statement = {
  bind: (...values: unknown[]) => D1Statement;
  all: <T>() => Promise<D1Result<T>>;
  first: <T>() => Promise<T | null>;
  run: () => Promise<unknown>;
};
type D1Database = {
  prepare: (query: string) => D1Statement;
  batch: (statements: D1Statement[]) => Promise<unknown>;
};

type Env = {
  DB: D1Database;
  OWNER_EMAIL?: string;
  EDITOR_EMAIL?: string;
  APP_ORIGIN?: string;
  TEAM_DOMAIN?: string;
  GOOGLE_DRIVE_CLIENT_ID?: string;
  GOOGLE_DRIVE_CLIENT_SECRET?: string;
  GOOGLE_DRIVE_REFRESH_TOKEN?: string;
  GOOGLE_DRIVE_BACKUP_FOLDER_ID?: string;
};

type AccessContext = { access?: { getIdentity?: () => Promise<{ email?: string } | null> } };
type Context = AccessContext;

type ContentInput = {
  id: string;
  title: string;
  kind: string;
  stage: string;
  due: string;
  next: string;
  accent: string;
  parentId: string | null;
  releaseAt?: string;
  sourceUrl?: string;
  scriptSections?: string[];
  assets?: { id: string; label: string; type: string; url: string; note?: string }[];
};

type TaskInput = {
  id: string;
  label: string;
  detail: string;
  done: boolean;
  contentId: string;
  dueAt?: string;
  requiresApproval: boolean;
};

const workspaceId = "nonstandard-answer";
const contentKinds = new Set(["Podcast", "長片", "Shorts", "SEO 文章", "IG 輪播", "FB 貼文", "復盤", "其他"]);
const stages = new Set(["靈感", "腳本", "製作中", "待發布", "已發布"]);
const accents = new Set(["purple", "pink", "lime", "blue"]);

function json(body: unknown, status = 200, request?: Request, env?: Env) {
  const headers = new Headers({ "content-type": "application/json; charset=utf-8", "cache-control": "no-store" });
  const origin = request?.headers.get("origin");
  const allowedOrigins = new Set((env?.APP_ORIGIN ?? "").split(",").map((value) => value.trim()).filter(Boolean));
  if (origin && allowedOrigins.has(origin)) {
    headers.set("access-control-allow-origin", origin);
    headers.set("access-control-allow-methods", "GET, POST, OPTIONS");
    headers.set("access-control-allow-headers", "content-type");
    headers.set("vary", "Origin");
  }
  return new Response(JSON.stringify(body), { status, headers });
}

function landingPage() {
  return new Response(`<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Creator OS 已驗證</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#191328;color:#f6f1ff;font-family:ui-sans-serif,system-ui,"Noto Sans TC",sans-serif}.card{max-width:36rem;padding:3rem;border:1px solid #66558a;border-radius:1.25rem;background:#241b36;box-shadow:0 2rem 5rem #090612}small{color:#bcb0d6;letter-spacing:.12em}h1{font-size:2rem;margin:.75rem 0}p{line-height:1.8;color:#ded5ed}code{padding:.2rem .4rem;border-radius:.3rem;background:#34264e;color:#edc8ff}</style><main class="card"><small>CREATOR OS · ACCESS VERIFIED</small><h1>驗證成功</h1><p>這個網址是雲端同步 API，不是工作站介面。請回到本機工作站 <code>http://localhost:3000</code>，再按「讀取雲端」。</p><p>第一次讀取若顯示雲端是空的，再按「一次性匯入本機資料」。</p></main></html>`, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store" } });
}

function normalizedEmail(value?: string) {
  return value?.trim().toLowerCase() ?? "";
}

async function memberFor(request: Request, env: Env, ctx: Context): Promise<{ email: string; role: Role } | Response> {
  // Static Assets routing does not expose ctx.access. Ask the Access identity
  // endpoint with the browser's cookie as a secure fallback.
  let identity = await ctx.access?.getIdentity?.();
  if (!identity?.email && env.TEAM_DOMAIN && request.headers.get("cookie")) {
    const headers = new Headers({ cookie: request.headers.get("cookie") as string });
    const assertion = request.headers.get("cf-access-jwt-assertion");
    if (assertion) headers.set("cf-access-jwt-assertion", assertion);
    const response = await fetch(`${env.TEAM_DOMAIN.replace(/\/$/, "")}/cdn-cgi/access/get-identity`, { headers });
    if (response.ok) identity = await response.json().then((value) => value as { email?: string }).catch(() => null);
  }
  const email = normalizedEmail(identity?.email);
  if (!email) return json({ error: "需要 Cloudflare Access 驗證。" }, 401, request, env);

  const ownerEmail = normalizedEmail(env.OWNER_EMAIL);
  if (!ownerEmail) return json({ error: "尚未設定 owner。" }, 503, request, env);

  let workspace = await env.DB.prepare("SELECT id FROM workspaces WHERE id = ?").bind(workspaceId).first<{ id: string }>();
  if (!workspace) {
    if (email !== ownerEmail) return json({ error: "工作區尚未由 owner 啟用。" }, 403, request, env);
    const statements = [
      env.DB.prepare("INSERT OR IGNORE INTO workspaces (id, name) VALUES (?, ?)").bind(workspaceId, "不標準答案"),
      env.DB.prepare("INSERT OR IGNORE INTO workspace_members (workspace_id, email, role) VALUES (?, ?, 'owner')").bind(workspaceId, ownerEmail),
    ];
    const editorEmail = normalizedEmail(env.EDITOR_EMAIL);
    if (editorEmail) statements.push(env.DB.prepare("INSERT OR IGNORE INTO workspace_members (workspace_id, email, role) VALUES (?, ?, 'editor')").bind(workspaceId, editorEmail));
    await env.DB.batch(statements);
    workspace = { id: workspaceId };
  }

  const member = await env.DB.prepare("SELECT email, role FROM workspace_members WHERE workspace_id = ? AND email = ?").bind(workspace.id, email).first<{ email: string; role: Role }>();
  return member ?? json({ error: "你不是這個工作區的成員。" }, 403, request, env);
}

function validContent(item: ContentInput) {
  const validAsset = (asset: NonNullable<ContentInput["assets"]>[number]) => typeof asset.id === "string" && typeof asset.label === "string" && asset.label.trim().length > 0 && typeof asset.type === "string" && typeof asset.url === "string" && /^https:\/\//.test(asset.url) && (asset.note === undefined || typeof asset.note === "string");
  return typeof item.id === "string" && typeof item.title === "string" && item.title.trim().length > 0 && item.title.length <= 180 && contentKinds.has(item.kind) && stages.has(item.stage) && typeof item.due === "string" && typeof item.next === "string" && accents.has(item.accent) && (item.parentId === null || typeof item.parentId === "string") && (item.releaseAt === undefined || typeof item.releaseAt === "string") && (item.sourceUrl === undefined || typeof item.sourceUrl === "string") && (item.scriptSections === undefined || (Array.isArray(item.scriptSections) && item.scriptSections.every((section) => typeof section === "string"))) && (item.assets === undefined || (Array.isArray(item.assets) && item.assets.every(validAsset)));
}

function validTask(item: TaskInput, contentIds: Set<string>) {
  return typeof item.id === "string" && typeof item.label === "string" && item.label.trim().length > 0 && item.label.length <= 180 && typeof item.detail === "string" && typeof item.done === "boolean" && contentIds.has(item.contentId) && typeof item.requiresApproval === "boolean" && (item.dueAt === undefined || typeof item.dueAt === "string");
}

async function state(env: Env) {
  const [contentRows, taskRows] = await Promise.all([
    env.DB.prepare("SELECT id, title, kind, stage, ui_due AS due, next_action AS next, accent, parent_id AS parentId, release_at AS releaseAt, source_url AS sourceUrl, script_sections AS scriptSections, assets_json AS assets FROM content_items WHERE workspace_id = ? ORDER BY created_at DESC").bind(workspaceId).all<ContentInput & { scriptSections?: string; assets?: string }>(),
    env.DB.prepare("SELECT id, title AS label, detail, status, content_item_id AS contentId, due_at AS dueAt, requires_approval AS requiresApproval FROM tasks WHERE workspace_id = ? ORDER BY due_at ASC, created_at ASC").bind(workspaceId).all<{ id: string; label: string; detail: string; status: string; contentId: string; dueAt?: string; requiresApproval: number }>(),
  ]);
  return {
    content: (contentRows.results ?? []).map((item) => ({ ...item, scriptSections: typeof item.scriptSections === "string" ? JSON.parse(item.scriptSections || "[]") : item.scriptSections, assets: typeof item.assets === "string" ? JSON.parse(item.assets || "[]") : item.assets })),
    tasks: (taskRows.results ?? []).map((task) => ({ ...task, done: task.status === "已完成", requiresApproval: Boolean(task.requiresApproval) })),
  };
}

function hex(bytes: ArrayBuffer) {
  return Array.from(new Uint8Array(bytes), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

function taipeiStamp(date: Date) {
  return new Intl.DateTimeFormat("sv-SE", {
    timeZone: "Asia/Taipei", year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
  }).format(date).replace(/[-: ]/g, "");
}

async function googleAccessToken(env: Env) {
  if (!env.GOOGLE_DRIVE_CLIENT_ID || !env.GOOGLE_DRIVE_CLIENT_SECRET || !env.GOOGLE_DRIVE_REFRESH_TOKEN || !env.GOOGLE_DRIVE_BACKUP_FOLDER_ID) {
    throw new Error("Google Drive 備份尚未完成授權設定。");
  }
  const form = new URLSearchParams({
    client_id: env.GOOGLE_DRIVE_CLIENT_ID,
    client_secret: env.GOOGLE_DRIVE_CLIENT_SECRET,
    refresh_token: env.GOOGLE_DRIVE_REFRESH_TOKEN,
    grant_type: "refresh_token",
  });
  const response = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: form,
  });
  const body = await response.json().catch(() => null) as { access_token?: string } | null;
  if (!response.ok || !body?.access_token) throw new Error("Google Drive 授權更新失敗。");
  return body.access_token;
}

async function backupToGoogleDrive(env: Env) {
  const workspace = await env.DB.prepare("SELECT id FROM workspaces WHERE id = ?").bind(workspaceId).first<{ id: string }>();
  if (!workspace) throw new Error("工作區尚未由 owner 啟用，無法建立備份。");

  const exportedAt = new Date().toISOString();
  const backupData = { schemaVersion: 1, workspaceId, exportedAt, state: await state(env) };
  const rawData = JSON.stringify(backupData);
  const sha256 = hex(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(rawData)));
  const fileName = `creator-os_${taipeiStamp(new Date())}.json`;
  const payload = JSON.stringify({ ...backupData, sha256 }, null, 2);
  const accessToken = await googleAccessToken(env);
  const boundary = `creator-os-${crypto.randomUUID()}`;
  const body = [
    `--${boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n`,
    JSON.stringify({ name: fileName, parents: [env.GOOGLE_DRIVE_BACKUP_FOLDER_ID], mimeType: "application/json", description: "Creator OS 自動異地備份" }),
    `\r\n--${boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n`,
    payload,
    `\r\n--${boundary}--`,
  ].join("");
  const response = await fetch("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,webViewLink", {
    method: "POST",
    headers: { authorization: `Bearer ${accessToken}`, "content-type": `multipart/related; boundary=${boundary}` },
    body,
  });
  const uploaded = await response.json().catch(() => null) as { id?: string } | null;
  if (!response.ok || !uploaded?.id) throw new Error("Google Drive 備份上傳失敗。");
  await env.DB.prepare("INSERT INTO backup_runs (id, workspace_id, destination, drive_file_id, file_name, size_bytes, sha256, status) VALUES (?, ?, 'google_drive', ?, ?, ?, ?, 'succeeded')")
    .bind(crypto.randomUUID(), workspaceId, uploaded.id, fileName, new TextEncoder().encode(payload).byteLength, sha256).run();
  return { id: uploaded.id, fileName, exportedAt, sha256 };
}

async function recordBackupFailure(env: Env, error: unknown) {
  const workspace = await env.DB.prepare("SELECT id FROM workspaces WHERE id = ?").bind(workspaceId).first<{ id: string }>();
  if (!workspace) return;
  const message = error instanceof Error ? error.message.slice(0, 500) : "Google Drive 備份失敗。";
  await env.DB.prepare("INSERT INTO backup_runs (id, workspace_id, destination, file_name, status, error_message) VALUES (?, ?, 'google_drive', ?, 'failed', ?)")
    .bind(crypto.randomUUID(), workspaceId, `creator-os_${taipeiStamp(new Date())}.json`, message).run().catch(() => undefined);
}

async function importState(request: Request, env: Env, email: string) {
  const payload = await request.json().catch(() => null) as { content?: ContentInput[]; tasks?: TaskInput[] } | null;
  if (!payload || !Array.isArray(payload.content) || !Array.isArray(payload.tasks)) return json({ error: "資料格式不正確。" }, 400, request, env);
  const contentIds = new Set(payload.content.map((item) => item.id));
  if (contentIds.size !== payload.content.length || !payload.content.every(validContent) || !payload.tasks.every((item) => validTask(item, contentIds))) return json({ error: "資料含有不支援的欄位或無效關聯。" }, 400, request, env);
  const existing = await env.DB.prepare("SELECT COUNT(*) AS count FROM content_items WHERE workspace_id = ?").bind(workspaceId).first<{ count: number }>();
  if ((existing?.count ?? 0) > 0) return json({ error: "雲端已有資料，為避免覆蓋，匯入只允許執行一次。" }, 409, request, env);

  const now = new Date().toISOString();
  const statements: D1Statement[] = [];
  for (const item of payload.content) {
    statements.push(env.DB.prepare("INSERT INTO content_items (id, workspace_id, parent_id, title, kind, stage, next_action, scheduled_at, ui_due, accent, release_at, source_url, script_sections, assets_json, created_by, updated_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(item.id, workspaceId, item.parentId, item.title.trim(), item.kind, item.stage, item.next, item.releaseAt ?? null, item.due, item.accent, item.releaseAt ?? null, item.sourceUrl ?? null, JSON.stringify(item.scriptSections ?? []), JSON.stringify(item.assets ?? []), email, email, now, now));
  }
  for (const item of payload.tasks) {
    statements.push(env.DB.prepare("INSERT INTO tasks (id, workspace_id, content_item_id, title, detail, status, due_at, requires_approval, completed_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(item.id, workspaceId, item.contentId, item.label.trim(), item.detail, item.done ? "已完成" : "待處理", item.dueAt ?? null, item.requiresApproval ? 1 : 0, item.done ? now : null, now, now));
  }
  if (statements.length) await env.DB.batch(statements);
  return json({ ok: true, imported: { content: payload.content.length, tasks: payload.tasks.length } }, 201, request, env);
}

async function replaceState(request: Request, env: Env, email: string, role: Role) {
  if (role === "viewer") return json({ error: "你沒有寫入工作區的權限。" }, 403, request, env);
  const payload = await request.json().catch(() => null) as { content?: ContentInput[]; tasks?: TaskInput[] } | null;
  if (!payload || !Array.isArray(payload.content) || !Array.isArray(payload.tasks)) return json({ error: "資料格式不正確。" }, 400, request, env);
  const contentIds = new Set(payload.content.map((item) => item.id));
  if (contentIds.size !== payload.content.length || !payload.content.every(validContent) || !payload.tasks.every((item) => validTask(item, contentIds))) return json({ error: "資料含有不支援的欄位或無效關聯。" }, 400, request, env);

  const now = new Date().toISOString();
  const statements: D1Statement[] = [
    env.DB.prepare("DELETE FROM tasks WHERE workspace_id = ?").bind(workspaceId),
    env.DB.prepare("DELETE FROM content_items WHERE workspace_id = ?").bind(workspaceId),
  ];
  for (const item of payload.content) {
    statements.push(env.DB.prepare("INSERT INTO content_items (id, workspace_id, parent_id, title, kind, stage, next_action, scheduled_at, ui_due, accent, release_at, source_url, script_sections, assets_json, created_by, updated_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(item.id, workspaceId, item.parentId, item.title.trim(), item.kind, item.stage, item.next, item.releaseAt ?? null, item.due, item.accent, item.releaseAt ?? null, item.sourceUrl ?? null, JSON.stringify(item.scriptSections ?? []), JSON.stringify(item.assets ?? []), email, email, now, now));
  }
  for (const item of payload.tasks) {
    statements.push(env.DB.prepare("INSERT INTO tasks (id, workspace_id, content_item_id, title, detail, status, due_at, requires_approval, completed_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(item.id, workspaceId, item.contentId, item.label.trim(), item.detail, item.done ? "已完成" : "待處理", item.dueAt ?? null, item.requiresApproval ? 1 : 0, item.done ? now : null, now, now));
  }
  await env.DB.batch(statements);
  return json({ ok: true, savedAt: now }, 200, request, env);
}

const worker = {
  async fetch(request: Request, env: Env, ctx: Context): Promise<Response> {
    if (request.method === "OPTIONS") return json({}, 204, request, env);
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/") return landingPage();
    if (url.pathname === "/health") return json({ ok: true }, 200, request, env);
    if (!url.pathname.startsWith("/v1/")) return json({ error: "找不到路徑。" }, 404, request, env);
    const member = await memberFor(request, env, ctx);
    if (member instanceof Response) return member;
    if (request.method === "GET" && url.pathname === "/v1/state") return json(await state(env), 200, request, env);
    if (request.method === "POST" && url.pathname === "/v1/import") return importState(request, env, member.email);
    if (request.method === "POST" && url.pathname === "/v1/state") return replaceState(request, env, member.email, member.role);
    if (request.method === "POST" && url.pathname === "/v1/backups") {
      if (member.role !== "owner") return json({ error: "只有 owner 可以建立異地備份。" }, 403, request, env);
      try {
        return json({ ok: true, backup: await backupToGoogleDrive(env) }, 201, request, env);
      } catch (error) {
        await recordBackupFailure(env, error);
        return json({ error: error instanceof Error ? error.message : "Google Drive 備份失敗。" }, 503, request, env);
      }
    }
    return json({ error: "不支援的操作。" }, 405, request, env);
  },
  async scheduled(_controller: unknown, env: Env) {
    try {
      await backupToGoogleDrive(env);
    } catch (error) {
      await recordBackupFailure(env, error);
    }
  },
};

export default worker;
