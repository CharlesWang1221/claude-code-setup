-- 保留 UI 所需的排期顯示、色彩與 Podcast 正片時間，避免匯入時遺失本機資料。
ALTER TABLE content_items ADD COLUMN ui_due TEXT;
ALTER TABLE content_items ADD COLUMN accent TEXT CHECK (accent IN ('purple', 'pink', 'lime', 'blue'));
ALTER TABLE content_items ADD COLUMN release_at TEXT;
