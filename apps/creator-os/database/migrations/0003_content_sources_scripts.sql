ALTER TABLE content_items ADD COLUMN source_url TEXT;
ALTER TABLE content_items ADD COLUMN script_sections TEXT NOT NULL DEFAULT '[]';
