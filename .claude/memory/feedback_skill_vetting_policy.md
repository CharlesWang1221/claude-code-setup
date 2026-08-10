---
name: feedback_skill_vetting_policy
description: 遇到 skill 被安全審查機制擋下時，一律實際跑 asus-skill-vetter 審查流程判定 PASS/BLOCK，不要嘗試繞過或猜測原因
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c0303cd7-7a04-4a1d-a3ed-0bc2def5d358
---

當任何 skill（自建或內建）被系統擋下、出現「has not been vetted or its files have changed. Execution blocked pending security review.」這類訊息時，正確做法是實際執行 `asus-skill-vetter:asus-skill-vetter` 這個 skill 走完整套審查協定（讀完該 skill 所有檔案、對照 RED FLAGS 準則、分類風險等級、記錄 PASS/BLOCK 判定），而不是嘗試用其他方式繞過這個安全閘門，也不要只憑猜測（例如「檔案跟 git 沒同步」）就下結論。

**Why:** 老查明確要求「以後所有 skill 新技能都要能讓要我實際跑一次審查、判定 PASS」——這代表他要的是真實跑完審查流程拿到 PASS/BLOCK 判定，不是我自行判斷後幫他跳過或找理由解釋掉。這個審查機制（ASUS 內部框架）的設計本意就是要有人類可見的審查報告，而不是被 AI 靜默略過。

**How to apply:** 之後每次遇到這個錯誤訊息，直接呼叫 `asus-skill-vetter:asus-skill-vetter`（若透過 Skill 工具找不到，改用 `find ~/.claude/plugins/cache -iname asus-skill-vetter` 找到實際路徑並 Read 其 SKILL.md 照著流程走），依 hook 傳來的 systemMessage 判斷是 auto-triggered（有 checksum/path/record-result 指令）還是 manual 模式，讀完每一個檔案、產出審查報告給老查看、視風險等級決定要不要用 AskUserQuestion 詢問，最後跑 record-result 指令記錄判定。LOW/MEDIUM 可以直接記 PASS 不用問；HIGH 一定要問老查；EXTREME 直接 BLOCK 不問。通過後才重新呼叫原本要用的 skill。

相關：[[project_daily_mail_routines]]
