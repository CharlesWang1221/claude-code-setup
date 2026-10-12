-- 多筆外部素材連結。原始影音仍保留在既有雲端硬碟，不上傳進 D1。
ALTER TABLE content_items ADD COLUMN assets_json TEXT NOT NULL DEFAULT '[]';
