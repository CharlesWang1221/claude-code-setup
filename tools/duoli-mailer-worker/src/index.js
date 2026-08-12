export default {
  async fetch(request, env) {
    if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405 });
    if (request.headers.get("Authorization") !== `Bearer ${env.DUOLI_WEBHOOK_TOKEN}`) {
      return new Response("Unauthorized", { status: 401 });
    }

    let report;
    try {
      report = await request.json();
    } catch {
      return new Response("Invalid JSON", { status: 400 });
    }

    if (!Array.isArray(report.to) || !report.to.length || typeof report.subject !== "string" || typeof report.html !== "string") {
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
