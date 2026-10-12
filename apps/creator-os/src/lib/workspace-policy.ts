export const CREATOR_OS_WORKSPACE = "不標準答案";

/**
 * Cloudflare Access 先擋住陌生帳號；Worker 收到請求後仍必須用這份名單
 * 驗證 email 是否為工作區成員，避免直接呼叫 API 時越權。
 */
export const invitedWorkspaceMembers = [
  { email: "debra.hdf@gmail.com", role: "editor" },
] as const;

/** 首次通過 Cloudflare Access 的老查帳號會被 Worker 建為 owner。 */
export const OWNER_BOOTSTRAP_RULE = "first-verified-access-email";

export type WorkspaceRole = "owner" | "editor" | "viewer";

export function canEdit(role: WorkspaceRole) {
  return role === "owner" || role === "editor";
}

export function canPublish(role: WorkspaceRole) {
  return role === "owner" || role === "editor";
}
