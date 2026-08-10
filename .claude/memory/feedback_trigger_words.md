---
name: feedback-trigger-words
description: 老查的專案觸發詞對照表——說特定關鍵字時要叫出哪個專案記憶繼續執行
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 272bf243-fe65-4c8e-add5-f9840da310d3
---

## 觸發詞規則

| 老查說 | 叫出的記憶/技能 | 動作 |
|---|---|---|
| 「做網頁」 | [[project-podcast-website]] | 讀取專案狀態，繼續執行待辦清單 |
| 「多利」 | skill: daily-routines-manager | 每日 cloud routine 排程總管，列出/新增/修改/暫停/測試每日寄送/寫入排程 |
| 「居易」 | skill: seo-article-writer | SEO文章撰寫手，關鍵字研究(Ahrefs)+文章撰寫+技術SEO檢查 |
| 「星期天」 | skill: podcast-publish | 單集上架統一入口，自動判斷這一集做到哪一步並接續執行到底 |

**Why:** 老查明確要求用關鍵字快速恢復專案上下文或叫出對應技能，不用每次重新說明。多利/居易/星期天是 skill 本身內建的觸發詞（非獨立記憶檔），2026-07-27 補記到觸發詞對照表方便統一查詢。
**How to apply:** 對話開頭偵測到觸發詞，若對應的是記憶則讀取確認狀態後問「從哪裡繼續？」；若對應的是 skill，直接用 Skill 工具叫出對應技能執行。
