const LOG_KEYS = [
  "ae-motion-graphics",
  "uiux-articles",
  "news-digest",
  "ai-startup-cases",
  "book-summaries",
  "podcast-direction",
  "competitor-monitor",
];

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/log/")) {
      return handleLog(request, env, url);
    }
    return handleSend(request, env);
  },
};

function checkAuth(request, env) {
  if (!env.DUOLI_WEBHOOK_TOKEN) return new Response("Mailer is not configured", { status: 503 });
  if (request.headers.get("Authorization") !== `Bearer ${env.DUOLI_WEBHOOK_TOKEN}`) {
    return new Response("Unauthorized", { status: 401 });
  }
  return null;
}

async function handleLog(request, env, url) {
  const authError = checkAuth(request, env);
  if (authError) return authError;
  if (!env.DUOLI_LOG) return new Response("Log store is not configured", { status: 503 });

  const key = url.pathname.slice("/log/".length);
  if (!LOG_KEYS.includes(key)) return new Response("Unknown log key", { status: 404 });

  if (request.method === "GET") {
    const value = await env.DUOLI_LOG.get(key);
    return new Response(value ?? "", { status: 200, headers: { "Content-Type": "text/plain; charset=utf-8" } });
  }

  if (request.method === "PUT" || request.method === "POST") {
    if (Number(request.headers.get("Content-Length") || 0) > 200_000) {
      return new Response("Payload Too Large", { status: 413 });
    }
    const body = await request.text();
    await env.DUOLI_LOG.put(key, body);
    return new Response("OK", { status: 200 });
  }

  return new Response("Method Not Allowed", { status: 405 });
}

async function handleSend(request, env) {
  if (!env.RESEND_API_KEY || !env.RESEND_FROM) {
    return new Response("Mailer is not configured", { status: 503 });
  }
  if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405 });
  if (request.headers.get("Content-Type")?.split(";", 1)[0] !== "application/json") {
    return new Response("Content-Type must be application/json", { status: 415 });
  }
  if (Number(request.headers.get("Content-Length") || 0) > 500_000) {
    return new Response("Payload Too Large", { status: 413 });
  }
  const authError = checkAuth(request, env);
  if (authError) return authError;

  let report;
  try {
    report = await request.json();
  } catch {
    return new Response("Invalid JSON", { status: 400 });
  }

  const allowedTo = ["siming1221@gmail.com"];
  const allowedCc = ["debra.hdf@gmail.com"];
  const toArray = (value) => (typeof value === "string" ? [value] : value);
  const isAllowed = (list, allowed) => Array.isArray(list) && list.every((email) => typeof email === "string" && allowed.includes(email.toLowerCase()));

  const to = toArray(report.to);
  const cc = report.cc === undefined ? undefined : toArray(report.cc);

  if (
    !isAllowed(to, allowedTo) || to.length !== 1 ||
    (cc !== undefined && !isAllowed(cc, allowedCc)) ||
    typeof report.subject !== "string" || !report.subject.startsWith("多利｜") || report.subject.length > 160 ||
    typeof report.html !== "string" || !report.html.trim() || report.html.length > 450_000
  ) {
    return new Response("Missing to, subject, or html", { status: 400 });
  }

  const payload = { from: env.RESEND_FROM, to, subject: report.subject, html: report.html };
  if (Array.isArray(cc) && cc.length) payload.cc = cc;

  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
      "Idempotency-Key": request.headers.get("Idempotency-Key") || crypto.randomUUID(),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) return new Response(await response.text(), { status: response.status });
  return new Response(JSON.stringify(await response.json()), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
