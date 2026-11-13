-- 總流量第一階段：集數 × 平台 × 觀察窗，手填或 CSV 匯入。
-- 口徑見 docs/briefs/CREATOR-OS-TRAFFIC-2026-11/BRIEF.md。不同平台的主要數字不得相加。
--
-- content_item_id 刻意不設外鍵：POST /v1/state 每次儲存會整批刪除再重建 content_items，
-- 若設外鍵（CASCADE 或 SET NULL），每次存工作站都會刪掉或斷開成效資料。
-- 集數以 episode（例：S4EP3）為主鍵的一部分；content_label 空字串代表集數本身，
-- 句剪等子內容填名稱（例：週二句剪）。

CREATE TABLE IF NOT EXISTS traffic_metrics (
  id TEXT PRIMARY KEY,
  workspace_id TEXT NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  episode TEXT NOT NULL CHECK (length(trim(episode)) BETWEEN 1 AND 40),
  content_label TEXT NOT NULL DEFAULT '' CHECK (length(content_label) <= 120),
  content_item_id TEXT,
  platform TEXT NOT NULL CHECK (platform IN ('Firstory', 'Spotify', 'Apple Podcasts', 'YouTube 正片', 'YouTube Shorts', 'FB', 'IG', 'Threads', '網站')),
  obs_window TEXT NOT NULL CHECK (obs_window IN ('D1', 'D7', 'D30')),
  primary_value INTEGER NOT NULL CHECK (primary_value >= 0),
  reach INTEGER CHECK (reach IS NULL OR reach >= 0),
  engagements INTEGER CHECK (engagements IS NULL OR engagements >= 0),
  link_clicks INTEGER CHECK (link_clicks IS NULL OR link_clicks >= 0),
  follower_delta INTEGER,
  source TEXT NOT NULL CHECK (source IN ('手填', 'CSV')),
  entered_by TEXT NOT NULL COLLATE NOCASE,
  note TEXT NOT NULL DEFAULT '' CHECK (length(note) <= 500),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (workspace_id, episode, content_label, platform, obs_window)
);

CREATE INDEX IF NOT EXISTS traffic_metrics_episode_idx ON traffic_metrics (workspace_id, episode);
