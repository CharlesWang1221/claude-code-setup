#!/usr/bin/env node
/**
 * 鐵雄稽核閘門：上傳前確認檔案有品管合規中心的 PASS 報告，且雜湊一致。
 *
 * CLI：
 *   node tools/qa-gate/qa-gate.cjs <要上傳的檔案> [--qa-report <報告路徑>]
 *   通過 exit 0；不通過 exit 1。輸出可直接貼進發布證據庫。
 *
 * 程式內：
 *   const { assertQaPass } = require('./qa-gate/qa-gate.cjs');
 *   assertQaPass(filePath, { report, projectRoot });  // 不通過會 throw
 *
 * 報告位置（依序尋找）：明確指定 → 檔案所在資料夾往上最多 3 層的 qa/report.md。
 * 報告格式見 codex/agents/qa_auditor.toml：需有「總結：PASS」與受檢檔的 SHA-256。
 *
 * 緊急放行：設定環境變數 QA_OVERRIDE_REASON="<理由>"。只有老查能決定推翻鐵雄，
 * 理由必須另寫入任務卡；每次放行都會記錄在 output/weekly-shorts/qa-overrides.log，由多利每日回報。
 */
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.resolve(__dirname, '..', '..');
const OVERRIDE_LOG = path.join(PROJECT_ROOT, 'output', 'weekly-shorts', 'qa-overrides.log');
const SUMMARY_RE = /總結\s*[:：]\s*(PASS|FAIL|UNVERIFIED)/;
const SHA_RE = /\b[0-9a-f]{64}\b/i;

function sha256(file) {
  const hash = crypto.createHash('sha256');
  const fd = fs.openSync(file, 'r');
  const buf = Buffer.alloc(1 << 20);
  try {
    let n;
    while ((n = fs.readSync(fd, buf, 0, buf.length, null)) > 0) hash.update(buf.subarray(0, n));
  } finally {
    fs.closeSync(fd);
  }
  return hash.digest('hex');
}

function findReport(file, explicit, projectRoot) {
  if (explicit) return path.resolve(projectRoot, explicit);
  let dir = path.dirname(path.resolve(file));
  const root = path.resolve(projectRoot);
  for (let i = 0; i <= 3; i++) {
    const candidate = path.join(dir, 'qa', 'report.md');
    if (fs.existsSync(candidate)) return candidate;
    const parent = path.dirname(dir);
    if (parent === dir || !parent.startsWith(root)) break;
    dir = parent;
  }
  return null;
}

/** 回傳 { ok, lines, report, sha }，不丟例外。 */
function checkQa(file, opts = {}) {
  const projectRoot = opts.projectRoot || PROJECT_ROOT;
  const rel = (p) => path.relative(projectRoot, p) || p;
  const lines = [];
  if (!file || !fs.existsSync(file)) {
    return { ok: false, lines: [`找不到要上傳的檔案：${file}`] };
  }
  const actual = sha256(file);
  lines.push(`檔案：${rel(path.resolve(file))}`);
  lines.push(`SHA-256：${actual}`);
  const report = findReport(file, opts.report, projectRoot);
  if (!report || !fs.existsSync(report)) {
    lines.push('結果：BLOCKED，找不到鐵雄稽核報告（qa/report.md）');
    return { ok: false, lines, sha: actual };
  }
  lines.push(`報告：${rel(report)}`);
  const text = fs.readFileSync(report, 'utf8');
  const summary = (text.match(SUMMARY_RE) || [])[1];
  const recorded = ((text.match(SHA_RE) || [])[0] || '').toLowerCase();
  if (summary !== 'PASS') {
    lines.push(`結果：BLOCKED，稽核總結為 ${summary || '（找不到總結）'}`);
    return { ok: false, lines, report, sha: actual };
  }
  if (!recorded) {
    lines.push('結果：BLOCKED，報告沒有記錄受檢檔的 SHA-256');
    return { ok: false, lines, report, sha: actual };
  }
  if (recorded !== actual) {
    lines.push(`結果：BLOCKED，報告審的是另一個版本（報告 ${recorded.slice(0, 12)}…，檔案 ${actual.slice(0, 12)}…）`);
    return { ok: false, lines, report, sha: actual };
  }
  lines.push('結果：PASS，鐵雄稽核通過且雜湊一致');
  return { ok: true, lines, report, sha: actual };
}

function logOverride(file, result, reason) {
  const stamp = new Date(Date.now() + 8 * 3600 * 1000).toISOString().replace('Z', '+08:00');
  const entry = [stamp, path.relative(PROJECT_ROOT, path.resolve(file)), result.sha || '', reason.replace(/\s+/g, ' ')].join('\t');
  fs.mkdirSync(path.dirname(OVERRIDE_LOG), { recursive: true });
  fs.appendFileSync(OVERRIDE_LOG, entry + '\n', 'utf8');
}

/** 不通過且沒有緊急放行時 throw；通過或放行時回傳結果。 */
function assertQaPass(file, opts = {}) {
  const result = checkQa(file, opts);
  for (const l of result.lines) console.log(`  [鐵雄閘門] ${l}`);
  if (result.ok) return result;
  const reason = (process.env.QA_OVERRIDE_REASON || '').trim();
  if (reason) {
    logOverride(file, result, reason);
    console.warn(`  [鐵雄閘門] ⚠ 緊急放行：${reason}（已記錄，理由須另寫入任務卡）`);
    return { ...result, overridden: true };
  }
  throw new Error('鐵雄稽核閘門未通過，已停止上傳。補齊 PASS 報告，或由老查決定以 QA_OVERRIDE_REASON 緊急放行。');
}

module.exports = { checkQa, assertQaPass, sha256 };

if (require.main === module) {
  const args = process.argv.slice(2);
  const i = args.indexOf('--qa-report');
  const report = i !== -1 ? args[i + 1] : undefined;
  const file = args.find((a, k) => !a.startsWith('--') && args[k - 1] !== '--qa-report');
  if (!file) {
    console.error('用法：node tools/qa-gate/qa-gate.cjs <要上傳的檔案> [--qa-report <報告路徑>]');
    process.exit(2);
  }
  const result = checkQa(file, { report });
  for (const l of result.lines) console.log(l);
  process.exit(result.ok ? 0 : 1);
}
