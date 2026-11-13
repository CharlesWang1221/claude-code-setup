import { csvToTrafficInputs, MAX_IMPORT_ROWS, trafficKey, validateTrafficInput, type TrafficInput, type TrafficRow, type TrafficSource } from "../../src/lib/traffic";

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
  LINE_CHANNEL_SECRET?: string;
  LINE_CHANNEL_ACCESS_TOKEN?: string;
  LINE_ALLOWED_USER_IDS?: string;
  LINE_PAIRING_CODE?: string;
  CREATOR_OS_WORKER_TOKEN?: string;
};

type RemoteCommand = {
  id: string;
  commandType: "run_workflow" | "approve" | "reject" | "pause";
  payload: Record<string, unknown>;
  status: string;
  createdAt: string;
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

async function ensureWorkspace(env: Env) {
  const existing = await env.DB.prepare("SELECT id FROM workspaces WHERE id = ?").bind(workspaceId).first<{ id: string }>();
  if (existing) return;
  const ownerEmail = normalizedEmail(env.OWNER_EMAIL);
  if (!ownerEmail) throw new Error("尚未設定 owner。");
  const statements = [
    env.DB.prepare("INSERT OR IGNORE INTO workspaces (id, name) VALUES (?, ?)").bind(workspaceId, "不標準答案"),
    env.DB.prepare("INSERT OR IGNORE INTO workspace_members (workspace_id, email, role) VALUES (?, ?, 'owner')").bind(workspaceId, ownerEmail),
  ];
  const editorEmail = normalizedEmail(env.EDITOR_EMAIL);
  if (editorEmail) statements.push(env.DB.prepare("INSERT OR IGNORE INTO workspace_members (workspace_id, email, role) VALUES (?, ?, 'editor')").bind(workspaceId, editorEmail));
  await env.DB.batch(statements);
}

function safeJson(value: string | null | undefined): Record<string, unknown> {
  if (!value) return {};
  try {
    const parsed = JSON.parse(value);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed as Record<string, unknown> : {};
  } catch {
    return {};
  }
}

async function remoteStatus(env: Env) {
  await ensureWorkspace(env);
  const [commands, workers] = await Promise.all([
    env.DB.prepare("SELECT id, command_type AS commandType, payload_json AS payloadJson, status, created_at AS createdAt FROM remote_commands WHERE workspace_id = ? ORDER BY created_at DESC LIMIT 6").bind(workspaceId).all<RemoteCommand & { payloadJson: string }>(),
    env.DB.prepare("SELECT id, label, status, last_seen_at AS lastSeenAt FROM remote_workers WHERE workspace_id = ? ORDER BY last_seen_at DESC").bind(workspaceId).all<{ id: string; label: string; status: string; lastSeenAt: string }>(),
  ]);
  const now = Date.now();
  return {
    commands: (commands.results ?? []).map(({ payloadJson, ...command }) => ({ ...command, payload: safeJson(payloadJson) })),
    workers: (workers.results ?? []).map((worker) => ({ ...worker, online: now - Date.parse(worker.lastSeenAt) < 90_000 })),
  };
}

async function createRemoteCommand(env: Env, requestedBy: string, commandType: RemoteCommand["commandType"], payload: Record<string, unknown>, idempotencyKey?: string) {
  await ensureWorkspace(env);
  const id = crypto.randomUUID();
  const now = new Date().toISOString();
  await env.DB.prepare("INSERT OR IGNORE INTO remote_commands (id, workspace_id, source, requested_by, command_type, payload_json, status, idempotency_key, created_at, updated_at) VALUES (?, ?, 'line', ?, ?, ?, 'queued', ?, ?, ?)")
    .bind(id, workspaceId, requestedBy, commandType, JSON.stringify(payload), idempotencyKey ?? null, now, now).run();
  if (idempotencyKey) {
    const saved = await env.DB.prepare("SELECT id, command_type AS commandType, payload_json AS payloadJson, status, created_at AS createdAt FROM remote_commands WHERE idempotency_key = ?").bind(idempotencyKey).first<RemoteCommand & { payloadJson: string }>();
    if (saved) return { ...saved, payload: safeJson(saved.payloadJson) };
  }
  return { id, commandType, payload, status: "queued", createdAt: now };
}

function configuredLineUsers(env: Env) {
  return (env.LINE_ALLOWED_USER_IDS ?? "").split(",").map((value) => value.trim()).filter(Boolean);
}

async function lineAllowed(userId: string, env: Env) {
  if (configuredLineUsers(env).includes(userId)) return true;
  await ensureWorkspace(env);
  const paired = await env.DB.prepare("SELECT user_id FROM line_authorized_users WHERE workspace_id = ? AND user_id = ?").bind(workspaceId, userId).first<{ user_id: string }>();
  return Boolean(paired);
}

async function pairLineUser(input: string, userId: string, env: Env) {
  const match = input.trim().match(/^配對\s+(.+)$/);
  if (!match || !env.LINE_PAIRING_CODE || match[1] !== env.LINE_PAIRING_CODE) return false;
  await ensureWorkspace(env);
  const now = new Date().toISOString();
  await env.DB.prepare("INSERT INTO line_authorized_users (workspace_id, user_id, label, paired_at, last_seen_at) VALUES (?, ?, '老查', ?, ?) ON CONFLICT(workspace_id, user_id) DO UPDATE SET last_seen_at = excluded.last_seen_at")
    .bind(workspaceId, userId, now, now).run();
  return true;
}

function commandHelp() {
  return "可用指令：\n進度\n待我核准\n執行 每日檢查\n核准 <命令 ID>\n退件 <命令 ID>：原因\n暫停 <命令 ID>";
}

function describeStatus(status: Awaited<ReturnType<typeof remoteStatus>>) {
  const online = status.workers.filter((worker) => worker.online);
  const workerText = online.length ? `Mac Worker：${online.map((worker) => `${worker.label}（${worker.status}）`).join("、")}` : "Mac Worker：離線，命令會保留在佇列。";
  const queued = status.commands.filter((command) => ["queued", "claimed", "running"].includes(command.status));
  const commandText = queued.length ? queued.map((command) => `${command.id.slice(0, 8)} ${command.commandType} ${command.status}`).join("\n") : "目前沒有待執行命令。";
  return `${workerText}\n\n待執行：\n${commandText}`;
}

async function lineSignatureValid(request: Request, secret: string) {
  const signature = request.headers.get("x-line-signature") ?? "";
  const body = await request.clone().text();
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const digest = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  const expected = btoa(String.fromCharCode(...new Uint8Array(digest)));
  if (signature.length !== expected.length) return false;
  let mismatch = 0;
  for (let index = 0; index < signature.length; index += 1) mismatch |= signature.charCodeAt(index) ^ expected.charCodeAt(index);
  return mismatch === 0;
}

async function lineReply(replyToken: string, text: string, env: Env) {
  if (!env.LINE_CHANNEL_ACCESS_TOKEN) throw new Error("LINE_CHANNEL_ACCESS_TOKEN 尚未設定。");
  const response = await fetch("https://api.line.me/v2/bot/message/reply", {
    method: "POST",
    headers: { authorization: `Bearer ${env.LINE_CHANNEL_ACCESS_TOKEN}`, "content-type": "application/json" },
    body: JSON.stringify({ replyToken, messages: [{ type: "text", text: text.slice(0, 4900) }] }),
  });
  if (!response.ok) throw new Error("LINE 回覆失敗。");
}

async function handleLineText(text: string, userId: string, eventId: string, env: Env) {
  const input = text.trim();
  if (["進度", "狀態"].includes(input)) return describeStatus(await remoteStatus(env));
  if (input === "待我核准") {
    const status = await remoteStatus(env);
    const waiting = status.commands.filter((command) => command.status === "queued");
    return waiting.length ? waiting.map((command) => `${command.id}\n${command.commandType} ${JSON.stringify(command.payload)}`).join("\n\n") : "目前沒有等待你決定的命令。";
  }
  if (/^執行\s*(每日檢查|daily-check)$/i.test(input)) {
    const command = await createRemoteCommand(env, userId, "run_workflow", { workflowId: "daily-check" }, eventId);
    return `已排入「每日檢查」。\n命令 ID：${command.id}\nMac 上線後會自動領取。`;
  }
  const approve = input.match(/^核准\s+([\w-]+)$/);
  if (approve) {
    const command = await createRemoteCommand(env, userId, "approve", { targetId: approve[1] }, eventId);
    return `已記錄核准命令：${command.id}`;
  }
  const reject = input.match(/^退件\s+([\w-]+)\s*[：:]\s*(.+)$/);
  if (reject) {
    const command = await createRemoteCommand(env, userId, "reject", { targetId: reject[1], reason: reject[2].slice(0, 1000) }, eventId);
    return `已記錄退件命令：${command.id}`;
  }
  const pause = input.match(/^暫停\s+([\w-]+)$/);
  if (pause) {
    const command = await createRemoteCommand(env, userId, "pause", { targetId: pause[1] }, eventId);
    return `已記錄暫停命令：${command.id}`;
  }
  return commandHelp();
}

async function handleLineWebhook(request: Request, env: Env) {
  if (!env.LINE_CHANNEL_SECRET || !env.LINE_CHANNEL_ACCESS_TOKEN) return new Response("LINE 尚未完成設定。", { status: 503 });
  if (!await lineSignatureValid(request, env.LINE_CHANNEL_SECRET)) return new Response("簽章無效。", { status: 401 });
  const body = await request.json().catch(() => null) as { events?: Array<{ type?: string; webhookEventId?: string; replyToken?: string; source?: { userId?: string }; message?: { type?: string; text?: string } }> } | null;
  for (const event of body?.events ?? []) {
    if (event.type !== "message" || event.message?.type !== "text" || !event.replyToken || !event.source?.userId) continue;
    const paired = await pairLineUser(event.message.text ?? "", event.source.userId, env);
    const allowed = paired || await lineAllowed(event.source.userId, env);
    const reply = paired ? "配對完成。這個 LINE 帳號已取得 Creator OS 遠端控制權限。輸入「進度」開始使用。" : allowed ? await handleLineText(event.message.text ?? "", event.source.userId, event.webhookEventId ?? crypto.randomUUID(), env) : "這個帳號沒有 Creator OS 遠端控制權限。請輸入由你在 Cloudflare 設定的配對碼。";
    await lineReply(event.replyToken, reply, env);
  }
  return new Response("OK");
}

function workerAuthorized(request: Request, env: Env) {
  const token = request.headers.get("authorization")?.replace(/^Bearer\s+/i, "");
  return Boolean(env.CREATOR_OS_WORKER_TOKEN && token && token === env.CREATOR_OS_WORKER_TOKEN);
}

async function claimRemoteCommand(request: Request, env: Env) {
  if (!workerAuthorized(request, env)) return json({ error: "Mac Worker 驗證失敗。" }, 401, request, env);
  await ensureWorkspace(env);
  const workerId = request.headers.get("x-creator-os-worker-id")?.trim();
  if (!workerId || workerId.length > 120) return json({ error: "缺少有效的 Worker ID。" }, 400, request, env);
  const body = await request.json().catch(() => ({})) as { label?: string };
  const now = new Date().toISOString();
  await env.DB.prepare("INSERT INTO remote_workers (id, workspace_id, label, status, last_seen_at, updated_at) VALUES (?, ?, ?, 'online', ?, ?) ON CONFLICT(id) DO UPDATE SET label = excluded.label, status = 'online', last_seen_at = excluded.last_seen_at, updated_at = excluded.updated_at")
    .bind(workerId, workspaceId, String(body.label ?? workerId).slice(0, 120), now, now).run();
  const next = await env.DB.prepare("SELECT id, command_type AS commandType, payload_json AS payloadJson, status, created_at AS createdAt FROM remote_commands WHERE workspace_id = ? AND status = 'queued' AND command_type = 'run_workflow' ORDER BY created_at ASC LIMIT 1").bind(workspaceId).first<RemoteCommand & { payloadJson: string }>();
  if (!next) return json({ command: null }, 200, request, env);
  await env.DB.prepare("UPDATE remote_commands SET status = 'claimed', worker_id = ?, claimed_at = ?, started_at = ?, updated_at = ? WHERE id = ? AND status = 'queued'").bind(workerId, now, now, now, next.id).run();
  const claimed = await env.DB.prepare("SELECT status FROM remote_commands WHERE id = ?").bind(next.id).first<{ status: string }>();
  if (claimed?.status !== "claimed") return json({ command: null }, 200, request, env);
  await env.DB.prepare("UPDATE remote_workers SET status = 'busy', current_command_id = ?, updated_at = ? WHERE id = ?").bind(next.id, now, workerId).run();
  return json({ command: { ...next, payload: safeJson(next.payloadJson) } }, 200, request, env);
}

async function completeRemoteCommand(request: Request, env: Env, commandId: string) {
  if (!workerAuthorized(request, env)) return json({ error: "Mac Worker 驗證失敗。" }, 401, request, env);
  const workerId = request.headers.get("x-creator-os-worker-id")?.trim();
  const body = await request.json().catch(() => null) as { ok?: boolean; result?: unknown; error?: string } | null;
  if (!workerId || !body || typeof body.ok !== "boolean") return json({ error: "完成回報格式錯誤。" }, 400, request, env);
  const now = new Date().toISOString();
  const status = body.ok ? "succeeded" : "failed";
  await env.DB.prepare("UPDATE remote_commands SET status = ?, result_json = ?, error_message = ?, completed_at = ?, updated_at = ? WHERE id = ? AND worker_id = ? AND status = 'claimed'")
    .bind(status, JSON.stringify(body.result ?? {}), body.ok ? null : String(body.error ?? "Mac Worker 執行失敗。").slice(0, 1000), now, now, commandId, workerId).run();
  await env.DB.prepare("UPDATE remote_workers SET status = 'online', current_command_id = NULL, last_seen_at = ?, updated_at = ? WHERE id = ?").bind(now, now, workerId).run();
  return json({ ok: true }, 200, request, env);
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

// ── 總流量（CREATOR-OS-TRAFFIC-2026-11 第一階段：手填＋CSV，不接平台 API）──

type TrafficDbRow = {
  id: string;
  episode: string;
  contentLabel: string;
  platform: TrafficRow["platform"];
  window: TrafficRow["window"];
  primaryValue: number;
  reach: number | null;
  engagements: number | null;
  linkClicks: number | null;
  followerDelta: number | null;
  source: TrafficSource;
  enteredBy: string;
  note: string;
  updatedAt: string;
};

async function listTraffic(env: Env): Promise<TrafficRow[]> {
  const rows = await env.DB.prepare("SELECT id, episode, content_label AS contentLabel, platform, obs_window AS window, primary_value AS primaryValue, reach, engagements, link_clicks AS linkClicks, follower_delta AS followerDelta, source, entered_by AS enteredBy, note, updated_at AS updatedAt FROM traffic_metrics WHERE workspace_id = ? ORDER BY episode DESC, content_label ASC, platform ASC, obs_window ASC").bind(workspaceId).all<TrafficDbRow>();
  return rows.results ?? [];
}

function upsertTrafficStatement(env: Env, input: TrafficInput, source: TrafficSource, email: string, now: string) {
  return env.DB.prepare("INSERT INTO traffic_metrics (id, workspace_id, episode, content_label, platform, obs_window, primary_value, reach, engagements, link_clicks, follower_delta, source, entered_by, note, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(workspace_id, episode, content_label, platform, obs_window) DO UPDATE SET primary_value = excluded.primary_value, reach = excluded.reach, engagements = excluded.engagements, link_clicks = excluded.link_clicks, follower_delta = excluded.follower_delta, source = excluded.source, entered_by = excluded.entered_by, note = excluded.note, updated_at = excluded.updated_at")
    .bind(crypto.randomUUID(), workspaceId, input.episode, input.contentLabel, input.platform, input.window, input.primaryValue, input.reach, input.engagements, input.linkClicks, input.followerDelta, source, email, input.note, now, now);
}

async function saveTrafficRow(request: Request, env: Env, email: string, role: Role) {
  if (role === "viewer") return json({ error: "你沒有寫入工作區的權限。" }, 403, request, env);
  const body = await request.json().catch(() => null) as Record<string, unknown> | null;
  if (!body || typeof body !== "object") return json({ error: "資料格式不正確。" }, 400, request, env);
  const { input, errors } = validateTrafficInput(body);
  if (!input) return json({ error: errors.join("；"), errors }, 400, request, env);
  await upsertTrafficStatement(env, input, "手填", email, new Date().toISOString()).run();
  return json({ ok: true, rows: await listTraffic(env) }, 200, request, env);
}

/** CSV 匯入兩段式：mode=preview 只回傳解析結果與錯誤列；mode=commit 全部無誤才寫入。 */
async function importTraffic(request: Request, env: Env, email: string, role: Role) {
  if (role === "viewer") return json({ error: "你沒有寫入工作區的權限。" }, 403, request, env);
  const body = await request.json().catch(() => null) as { csv?: unknown; mode?: unknown } | null;
  if (!body || typeof body.csv !== "string" || (body.mode !== "preview" && body.mode !== "commit")) return json({ error: "需要 csv 文字與 mode（preview 或 commit）。" }, 400, request, env);
  if (body.csv.length > 512_000) return json({ error: "CSV 超過 500 KB。" }, 413, request, env);

  const { inputs, errors } = csvToTrafficInputs(body.csv);
  const existing = new Set((await listTraffic(env)).map(trafficKey));
  const overwrites = inputs.filter((input) => existing.has(trafficKey(input))).length;
  const summary = { rows: inputs, errors, total: inputs.length, overwrites, inserts: inputs.length - overwrites, maxRows: MAX_IMPORT_ROWS };
  if (body.mode === "preview") return json({ ok: true, ...summary }, 200, request, env);

  if (errors.length) return json({ error: "CSV 有錯誤列，請修正後重新預覽，未寫入任何資料。", ...summary }, 400, request, env);
  if (!inputs.length) return json({ error: "CSV 沒有資料列。" }, 400, request, env);
  const now = new Date().toISOString();
  await env.DB.batch(inputs.map((input) => upsertTrafficStatement(env, input, "CSV", email, now)));
  return json({ ok: true, imported: inputs.length, overwrites, rows: await listTraffic(env) }, 200, request, env);
}

const worker = {
  async fetch(request: Request, env: Env, ctx: Context): Promise<Response> {
    if (request.method === "OPTIONS") return json({}, 204, request, env);
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/") return landingPage();
    if (url.pathname === "/health") return json({ ok: true }, 200, request, env);
    if (request.method === "POST" && url.pathname === "/line/webhook") return handleLineWebhook(request, env);
    if (request.method === "POST" && url.pathname === "/v1/worker/claim") return claimRemoteCommand(request, env);
    const completedCommand = url.pathname.match(/^\/v1\/worker\/commands\/([\w-]+)\/complete$/);
    if (request.method === "POST" && completedCommand) return completeRemoteCommand(request, env, completedCommand[1]);
    if (!url.pathname.startsWith("/v1/")) return json({ error: "找不到路徑。" }, 404, request, env);
    const member = await memberFor(request, env, ctx);
    if (member instanceof Response) return member;
    if (request.method === "GET" && url.pathname === "/v1/state") return json(await state(env), 200, request, env);
    if (request.method === "GET" && url.pathname === "/v1/remote/status") return json(await remoteStatus(env), 200, request, env);
    if (request.method === "POST" && url.pathname === "/v1/import") return importState(request, env, member.email);
    if (request.method === "POST" && url.pathname === "/v1/state") return replaceState(request, env, member.email, member.role);
    if (request.method === "GET" && url.pathname === "/v1/traffic") return json({ rows: await listTraffic(env), role: member.role }, 200, request, env);
    if (request.method === "POST" && url.pathname === "/v1/traffic") return saveTrafficRow(request, env, member.email, member.role);
    if (request.method === "POST" && url.pathname === "/v1/traffic/import") return importTraffic(request, env, member.email, member.role);
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
