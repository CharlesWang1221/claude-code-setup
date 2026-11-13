-- 首次配對完成的 LINE 帳號。配對碼是一次性人工授權，之後仍可由環境白名單補充。
CREATE TABLE IF NOT EXISTS line_authorized_users (
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  label TEXT,
  paired_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (workspace_id, user_id)
);

CREATE INDEX IF NOT EXISTS line_authorized_users_workspace_seen_idx ON line_authorized_users (workspace_id, last_seen_at);
