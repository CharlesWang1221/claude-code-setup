---
name: project_daily_mail_routines_zapier_quota
description: 8/8起多利每日排程寄信全部失效的根因(Zapier MCP task額度爆表)、已做的調整、還沒解決的部分
metadata: 
  node_type: memory
  type: project
  originSessionId: c0303cd7-7a04-4a1d-a3ed-0bc2def5d358
---

## 根因（2026-08-10 確認）
老查所有每日排程（多利管理，見 `daily-routines-manager` skill）從 2026-08-08 起完全沒有任何一封信寄達，排程本身顯示「已觸發」但零輸出零錯誤。查到的真正原因：**Zapier MCP 帳號的 task 額度爆表**（Zapier 網頁後台「Claude MCP Server」頁面顯示 Plan tasks 102/100，resets in 4 weeks）。每個排程執行一次要打 2-3 次 Zapier task（確認動作可用/查防重複/寄信），7 個每日排程疊起來一天燒 15-20+ tasks，100 額度撐不了幾天。

**Why:** 額度是帳號層級共用的，不是單一排程的問題，也不是 Anthropic 平台側的 bug（一開始誤判是 skill 安全審查機制`asus-skill-vetter`造成的，後來證實是巧合，那個審查機制是另一件事、已經處理完成，跟這個額度問題無關）。
**How to apply:** 之後老查再問「為什�麼沒收到信」，先查 Zapier 網頁後台的 task 額度用量，不要再猜測是排程內容或平台審查問題。

## 已做的調整（2026-08-10）
1. 7 個寄信類排程都拿掉了多餘的「確認 Gmail 動作可用」檢查步驟（`list_enabled_zapier_actions`），只留「查防重複」+「寄信」兩步，每次執行省 1 個 task。過程中手動編輯長篇中文 prompt 出過兩次亂碼事故（daily-competitor-monitor-7 被打壞兩次），最後改用 Python 腳本讀本機備份檔+`jq`式 ASCII escape 再貼上的機械化方式才穩定成功，之後這種長中文內容編輯應該優先用這個方法，不要手動重打。
2. 為了讓額度撐更久，調整了執行頻率（trigger_id 對照見 `daily-routines-manager` skill 的 `routines/README.md`）：
   - 維持每天：daily-news-digest-15（新聞，改成隔天單數日 `0 0 */2 * *`）、daily-ae-motion-graphics-report（AE影片，仍每天）
   - 改每週一（`0 0 * * 1`）：daily-book-summaries-3（書摘）、daily-ai-startup-cases-report（AI創業案例）、daily-podcast-direction-inspiration-report（每次創作靈感）
   - 改每月 1、15 號（`0 0 1,15 * *`）：daily-competitor-monitor-7（競品監控）、daily-uiux-articles-report（UIUX）
3. 本機備份檔 `routines/*.md` **還沒同步**這次的內容/cron改動，還是舊版，之後要記得同步+commit。

## 還沒解決的部分
- 就算做完上述調整，估算約 125 tasks/月，仍超過 100 額度的 25%，沒有完全解決（AE影片維持每天是最大單一貢獻者，60 tasks/月）。
- 老查說「先這樣，等額度能使用就馬上幫我執行」——但**沒有工具可以自動偵測 Zapier 額度是否已重置/升級**，只能等老查自己去 Zapier 後台看、跟我說了才能手動測試確認恢復。
- `影片分析每日推薦`（trig_01WoF3zy2i2AVHdhBSHhtQa6，寫入 GitHub repo「影片分析」分支，不用 Zapier）是另一個獨立問題：從建立（7/21）以來從未成功 push 過一次 commit，該分支在 remote 上不存在，跟這次 Zapier 額度問題無關，還沒查為什麼。

相關：[[feedback_skill_vetting_policy]]
