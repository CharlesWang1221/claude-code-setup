-- LINE 遠端控制與 Mac Worker 佇列。LINE 只能建立受白名單保護的命令；
-- Mac 主動領取命令，因此不需要開放家中電腦的入站連線。

CREATE TABLE IF NOT EXISTS remote_commands (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  source TEXT NOT NULL CHECK (source IN ('line', 'web', 'system')),
  requested_by TEXT NOT NULL,
  command_type TEXT NOT NULL CHECK (command_type IN ('run_workflow', 'approve', 'reject', 'pause')),
  payload_json TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL CHECK (status IN ('queued', 'claimed', 'running', 'succeeded', 'failed', 'cancelled')) DEFAULT 'queued',
  idempotency_key TEXT UNIQUE,
  worker_id TEXT,
  result_json TEXT,
  error_message TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  claimed_at TEXT,
  started_at TEXT,
  completed_at TEXT,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS remote_workers (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('online', 'offline', 'busy')) DEFAULT 'offline',
  last_seen_at TEXT NOT NULL,
  current_command_id TEXT REFERENCES remote_commands(id) ON DELETE SET NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS remote_commands_workspace_status_idx ON remote_commands (workspace_id, status, created_at);
CREATE INDEX IF NOT EXISTS remote_workers_workspace_seen_idx ON remote_workers (workspace_id, last_seen_at);
