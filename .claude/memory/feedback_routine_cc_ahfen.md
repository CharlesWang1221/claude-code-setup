---
name: feedback-routine-cc-ahfen
description: 跟節目內容策略相關的每日排程 mail，預設要 CC 給阿分
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5f7f211b-f8db-49b5-a1bf-bc626520a9f1
---

跟《不標準答案》內容策略、創作方向、競品動態相關的每日排程 mail，預設都要 CC 給阿分（debra.hdf@gmail.com），不是只寄給老查一人。目前已套用的排程：daily-ai-startup-cases-report、daily-podcast-direction-inspiration-report、daily-competitor-monitor-4（2026-08-03 補加）。

**Why:** 阿分是《不標準答案》共同主持人，這類報告是節目共同決策的參考資料，老查明確要求以後也要同步備份給阿分看，不要只有他單邊看到。
**How to apply:** 用 [[daily-routines-manager]]（多利）新增或修改跟內容策略/創作方向/競品分析相關的 mail routine 時，預設在 gmail_send_email 加上 cc: debra.hdf@gmail.com（維持老查 to、阿分 cc 的主寄件人結構，不要兩人平行主收件人）。跟內容策略無關的排程（例如純技術類、書籍摘要以外的其他用途）不用預設套用，遇到不確定的新排程時跟老查確認一次即可。
