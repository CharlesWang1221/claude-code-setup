#!/usr/bin/env node
import fs from "node:fs/promises";
import http from "node:http";
import { spawn } from "node:child_process";
import process from "node:process";
import { URL, fileURLToPath } from "node:url";

const jsonPath = process.argv[2];
const configure = process.argv[3] === "--configure";
const folderId = process.argv[4];
const creatorOsDir = fileURLToPath(new URL("../", import.meta.url));
if (!jsonPath) {
  console.error("用法：node tools/google-drive-oauth.mjs <Google 下載的 OAuth JSON 路徑>");
  process.exit(1);
}
const raw = JSON.parse(await fs.readFile(jsonPath, "utf8"));
const credentials = raw.installed ?? raw.web;
if (!credentials?.client_id || !credentials?.client_secret) throw new Error("找不到 OAuth client_id 或 client_secret。");

const server = http.createServer();
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const address = server.address();
if (!address || typeof address === "string") throw new Error("無法建立本機 OAuth 回呼連線。");
const redirectUri = `http://127.0.0.1:${address.port}/oauth2callback`;
const authUrl = new URL("https://accounts.google.com/o/oauth2/v2/auth");
authUrl.searchParams.set("client_id", credentials.client_id);
authUrl.searchParams.set("redirect_uri", redirectUri);
authUrl.searchParams.set("response_type", "code");
authUrl.searchParams.set("scope", "https://www.googleapis.com/auth/drive.file");
authUrl.searchParams.set("access_type", "offline");
authUrl.searchParams.set("prompt", "consent");

console.log("請複製以下網址到瀏覽器，用老查的 Google 帳號完成授權：");
console.log(authUrl.toString());
console.log("授權完成後回到這個視窗，工具會顯示 refresh token。不要把 token 貼到聊天或提交 Git。");

const code = await new Promise((resolve, reject) => {
  const timer = setTimeout(() => reject(new Error("OAuth 授權逾時，請重新執行。")), 20 * 60 * 1000);
  server.on("request", (request, response) => {
    const requestUrl = new URL(request.url ?? "/", `http://${request.headers.host}`);
    if (requestUrl.pathname !== "/oauth2callback") return;
    const error = requestUrl.searchParams.get("error");
    if (error) { clearTimeout(timer); response.end("授權失敗，可以關閉這個分頁。\n"); reject(new Error(`Google OAuth 失敗：${error}`)); return; }
    const value = requestUrl.searchParams.get("code");
    if (!value) return;
    clearTimeout(timer); response.end("Creator OS 授權完成，可以關閉這個分頁。\n"); resolve(value);
  });
});
server.close();

const tokenResponse = await fetch("https://oauth2.googleapis.com/token", {
  method: "POST",
  headers: { "content-type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({ client_id: credentials.client_id, client_secret: credentials.client_secret, code, grant_type: "authorization_code", redirect_uri: redirectUri }),
});
const token = await tokenResponse.json();
if (!tokenResponse.ok || !token.refresh_token) throw new Error(`換取 refresh token 失敗：${token.error ?? tokenResponse.status}`);

if (configure) {
  if (!folderId) throw new Error("--configure 必須同時提供 Google Drive 備份資料夾 ID。");
  const putSecret = (name, value) => new Promise((resolve, reject) => {
    const command = process.platform === "win32" ? "npx.cmd" : "npx";
    const child = spawn(command, ["wrangler", "secret", "put", name], { cwd: creatorOsDir, shell: process.platform === "win32", stdio: ["pipe", "inherit", "inherit"] });
    child.on("error", reject);
    child.on("exit", (code) => code === 0 ? resolve() : reject(new Error(`設定 Cloudflare Secret ${name} 失敗。`)));
    child.stdin.end(value);
  });
  await putSecret("GOOGLE_DRIVE_CLIENT_ID", credentials.client_id);
  await putSecret("GOOGLE_DRIVE_CLIENT_SECRET", credentials.client_secret);
  await putSecret("GOOGLE_DRIVE_REFRESH_TOKEN", token.refresh_token);
  await putSecret("GOOGLE_DRIVE_BACKUP_FOLDER_ID", folderId);
  console.log("Google Drive 備份的 Cloudflare Secrets 已設定完成。");
} else {
  console.log(`\nGOOGLE_DRIVE_CLIENT_ID=${credentials.client_id}`);
  console.log(`GOOGLE_DRIVE_CLIENT_SECRET=${credentials.client_secret}`);
  console.log(`GOOGLE_DRIVE_REFRESH_TOKEN=${token.refresh_token}`);
}
