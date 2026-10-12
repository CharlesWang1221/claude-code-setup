-- Creator OS：Cloudflare D1 資料模型
-- 本檔只定義資料。入口權限交給 Cloudflare Access，並只允許老查與阿分帳號。
-- 在建立 D1 database 後執行：wrangler d1 migrations apply creator-os --remote

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS workspaces (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workspace_members (
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  email TEXT NOT NULL COLLATE NOCASE,
  role TEXT NOT NULL CHECK (role IN ('owner', 'editor', 'viewer')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (workspace_id, email)
);

CREATE TABLE IF NOT EXISTS content_items (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  parent_id TEXT REFERENCES content_items(id) ON DELETE SET NULL,
  title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 180),
  kind TEXT NOT NULL CHECK (kind IN ('Podcast', '長片', 'Shorts', 'SEO 文章', 'IG 輪播', 'FB 貼文', '復盤', '其他')),
  stage TEXT NOT NULL CHECK (stage IN ('靈感', '腳本', '製作中', '待發布', '已發布')) DEFAULT '靈感',
  next_action TEXT,
  scheduled_at TEXT,
  published_at TEXT,
  created_by TEXT NOT NULL COLLATE NOCASE,
  updated_by TEXT NOT NULL COLLATE NOCASE,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  content_item_id TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
  title TEXT NOT NULL CHECK (length(trim(title)) BETWEEN 1 AND 180),
  detail TEXT,
  status TEXT NOT NULL CHECK (status IN ('待處理', '進行中', '已完成', '已取消')) DEFAULT '待處理',
  due_at TEXT,
  requires_approval INTEGER NOT NULL DEFAULT 0 CHECK (requires_approval IN (0, 1)),
  approved_at TEXT,
  approved_by TEXT COLLATE NOCASE,
  completed_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  content_item_id TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
  label TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  google_drive_url TEXT NOT NULL CHECK (google_drive_url LIKE 'https://%'),
  version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
  approved_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS publications (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  content_item_id TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('草稿', '待核准', '已排程', '已發布', '失敗')),
  scheduled_at TEXT,
  published_at TEXT,
  external_url TEXT CHECK (external_url IS NULL OR external_url LIKE 'https://%'),
  external_id TEXT,
  approval_required INTEGER NOT NULL DEFAULT 1 CHECK (approval_required IN (0, 1)),
  approved_at TEXT,
  approved_by TEXT COLLATE NOCASE,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (content_item_id, platform)
);

CREATE TABLE IF NOT EXISTS metric_snapshots (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  publication_id TEXT NOT NULL REFERENCES publications(id) ON DELETE CASCADE,
  captured_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  age_days INTEGER NOT NULL CHECK (age_days IN (3, 7, 30)),
  plays INTEGER CHECK (plays >= 0),
  reach INTEGER CHECK (reach >= 0),
  engagements INTEGER CHECK (engagements >= 0),
  completion_rate REAL CHECK (completion_rate BETWEEN 0 AND 100),
  raw_metrics TEXT NOT NULL DEFAULT '{}',
  UNIQUE (publication_id, age_days)
);

CREATE TABLE IF NOT EXISTS reviews (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  content_item_id TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
  effective_note TEXT,
  improvement_note TEXT,
  proposed_rule TEXT,
  rule_approved_at TEXT,
  rule_approved_by TEXT COLLATE NOCASE,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS content_items_workspace_scheduled_idx ON content_items (workspace_id, scheduled_at);
CREATE INDEX IF NOT EXISTS content_items_parent_idx ON content_items (parent_id);
CREATE INDEX IF NOT EXISTS tasks_workspace_due_idx ON tasks (workspace_id, due_at, status);
CREATE INDEX IF NOT EXISTS workspace_members_email_idx ON workspace_members (email);
