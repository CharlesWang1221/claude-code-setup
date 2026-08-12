export default {
  async fetch(request, env) {
    if (!env.DUOLI_WEBHOOK_TOKEN || !env.RESEND_API_KEY || !env.RESEND_FROM) {
      return new Response("Mailer is not configured", { status: 503 });
    }
    if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405 });
    if (request.headers.get("Content-Type")?.split(";", 1)[0] !== "application/json") {
      return new Response("Content-Type must be application/json", { status: 415 });
    }
    if (Number(request.headers.get("Content-Length") || 0) > 500_000) {
      return new Response("Payload Too Large", { status: 413 });
    }
    if (request.headers.get("Authorization") !== `Bearer ${env.DUOLI_WEBHOOK_TOKEN}`) {
      return new Response("Unauthorized", { status: 401 });
    }

    let report;
    try {
      report = await request.json();
    } catch {
      return new Response("Invalid JSON", { status: 400 });
    }

    const allowedTo = ["siming1221@gmail.com"];
    const allowedCc = ["debra.hdf@gmail.com"];
    const isAllowed = (list, allowed) => Array.isArray(list) && list.every((email) => typeof email === "string" && allowed.includes(email.toLowerCase()));

    if (
      !isAllowed(report.to, allowedTo) || report.to.length !== 1 ||
      (report.cc !== undefined && !isAllowed(report.cc, allowedCc)) ||
      typeof report.subject !== "string" || !report.subject.startsWith("多利｜") || report.subject.length > 160 ||
      typeof report.html !== "string" || !report.html.trim() || report.html.length > 450_000
    ) {
      return new Response("Missing to, subject, or html", { status: 400 });
    }

    const payload = { from: env.RESEND_FROM, to: report.to, subject: report.subject, html: report.html };
    if (Array.isArray(report.cc) && report.cc.length) payload.cc = report.cc;

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
  },
};
