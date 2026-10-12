-- 異地備份執行紀錄。實際快照檔放在 Google Drive，不放進 D1。
CREATE TABLE IF NOT EXISTS backup_runs (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  destination TEXT NOT NULL CHECK (destination IN ('google_drive')),
  drive_file_id TEXT,
  file_name TEXT NOT NULL,
  size_bytes INTEGER,
  sha256 TEXT,
  status TEXT NOT NULL CHECK (status IN ('succeeded', 'failed')),
  error_message TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS backup_runs_workspace_created_idx
  ON backup_runs (workspace_id, created_at DESC);
