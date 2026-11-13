#!/usr/bin/env node
/**
 * Creator OS 的 Mac 常駐 Worker。
 * 它只向 Cloudflare 拉取工作，不開放任何入站連線；只執行設定檔內明確允許的 workflow。
 */
import { readFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const configPath = process.env.CREATOR_OS_WORKER_CONFIG ?? resolve(here, "worker-config.json");
const config = JSON.parse(await readFile(configPath, "utf8"));
const required = ["apiUrl", "workerId", "workerToken"];
for (const field of required) if (!config[field]) throw new Error(`worker-config.json 缺少 ${field}`);

const apiUrl = config.apiUrl.replace(/\/$/, "");
const wait = (ms) => new Promise((done) => setTimeout(done, ms));

async function api(path, init = {}) {
  const response = await fetch(`${apiUrl}${path}`, {
    ...init,
    headers: {
      authorization: `Bearer ${config.workerToken}`,
      "content-type": "application/json",
      "x-creator-os-worker-id": config.workerId,
      ...init.headers,
    },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error ?? `遠端請求失敗 (${response.status})`);
  return body;
}

function execute(workflow) {
  return new Promise((resolvePromise) => {
    const child = spawn(workflow.command, workflow.args ?? [], {
      cwd: workflow.cwd ?? process.cwd(),
      env: { ...process.env, ...(workflow.env ?? {}) },
      shell: false,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let output = "";
    const append = (chunk) => { output = `${output}${chunk}`.slice(-12000); };
    child.stdout.on("data", append);
    child.stderr.on("data", append);
    child.on("error", (error) => resolvePromise({ ok: false, output: error.message }));
    child.on("close", (code) => resolvePromise({ ok: code === 0, output, code }));
  });
}

async function loop() {
  for (;;) {
    try {
      const claimed = await api("/v1/worker/claim", { method: "POST", body: JSON.stringify({ label: config.label ?? "Mac" }) });
      if (!claimed.command) {
        await wait(config.pollIntervalMs ?? 15000);
        continue;
      }
      const command = claimed.command;
      const workflowId = command.payload?.workflowId;
      const workflow = config.workflows?.[workflowId];
      if (command.commandType !== "run_workflow" || !workflow) {
        await api(`/v1/worker/commands/${command.id}/complete`, { method: "POST", body: JSON.stringify({ ok: false, error: `未授權或不存在的 workflow：${workflowId ?? "未知"}` }) });
        continue;
      }
      const result = await execute(workflow);
      await api(`/v1/worker/commands/${command.id}/complete`, { method: "POST", body: JSON.stringify({ ok: result.ok, result: { exitCode: result.code, output: result.output }, error: result.ok ? undefined : `workflow ${workflowId} 執行失敗` }) });
    } catch (error) {
      console.error(new Date().toISOString(), error instanceof Error ? error.message : error);
      await wait(config.pollIntervalMs ?? 15000);
    }
  }
}

loop();
