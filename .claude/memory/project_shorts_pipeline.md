---
name: project-shorts-pipeline
description: 短影音自動剪輯 pipeline（Whisper→Auto-Editor→Pexels B-roll→FFmpeg 三區版型→YouTube），s2ep7 已完成首支
metadata: 
  node_type: memory
  type: project
  originSessionId: b76b13ca-5be2-4f8a-98da-1f1e32acb072
---

## 短影音 Pipeline 工具鏈

**工具目錄**：`D:/hot data/CCoode/tools/video-auto-edit/`
**腳本**：
- `scripts/fetch_broll.py` — Pexels B-roll 下載，支援 `--keywords` 手動指定英文關鍵字
- `scripts/srt_to_drawtext.js` — SRT → FFmpeg drawtext filter chain
- `C:/tmp/{專案}/build_broll_filter.js` — 產生完整 FFmpeg filter + 指令（每次手動建在 tmp）

**Windows 注意事項**：
- 路徑有空格 → 先複製到 `C:/tmp/{專案名}/` 再跑 FFmpeg
- 字型用 `fontfile='C\\:/Windows/Fonts/NotoSansTC-VF.ttf'`（Windows 無 fontconfig）
- Python 完整路徑：`C:/Users/siming_wang/AppData/Local/Programs/Python/Python312/python.exe`

**Why:** 觸發詞「剪短影片」「做 Shorts」時啟用此流程

---

## s2ep7-short 第一支 Shorts（待修改）

**專案路徑**：`D:/hot data/CCoode/video-projects/s2ep7-short/`
**主題**：校園廁所偷拍事件、隱私、監視器
**YouTube 影片 ID**：`YYo8tIb8FFU`
**YouTube Studio**：https://studio.youtube.com/video/YYo8tIb8FFU/edit
**目前狀態**：私人（private）—— 待確認內容後改公開

**影片資訊**：
- 時長：約 42 秒（Auto-Editor 剪靜音後）
- 尺寸：1080×1920（垂直 Shorts 格式）
- 標題（目前）：你進廁所？第一眼看到什麼 #Shorts
- CTA：追蹤《不標準答案》Podcast

**B-roll 三個插入點**：
- 10.7s「為什麼上班會有同事投拍你」→ security camera office
- 17.4s「我覺得你不沈重，你是武裝」→ anxiety stressed
- 24.8s「如果萬一是家人被嚇」→ family worried

**待修改事項**：需確認影片內容、標題/說明欄、公開時間

**How to apply:** 提到「s2ep7 短影音」、「那支 Shorts」、「YYo8tIb8FFU」時直接帶出此資訊
