---
name: feedback-trigger-words
description: 老查的專案觸發詞對照表——說特定關鍵字時要叫出哪個專案記憶繼續執行
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 272bf243-fe65-4c8e-add5-f9840da310d3
---

## 觸發詞規則

| 老查說 | 叫出的記憶 | 動作 |
|---|---|---|
| 「做網頁」 | [[project-podcast-website]] | 讀取專案狀態，繼續執行待辦清單 |

**Why:** 老查明確要求用關鍵字快速恢復專案上下文，不用每次重新說明。
**How to apply:** 對話開頭偵測到觸發詞，立即讀取對應記憶，確認目前狀態後問「從哪裡繼續？」或直接提示待辦清單。
