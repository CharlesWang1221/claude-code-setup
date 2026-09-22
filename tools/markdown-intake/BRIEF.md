---
task_id: WORKFLOW-MARKDOWN-INTAKE
status: LOCKED
owner: 系統與資產總監
created_at: 2026-09-22 10:49 Asia/Taipei
last_updated: 2026-09-22 12:17 Asia/Taipei
---

# 文件 Markdown 入口

## 目標與完成定義

- 要解決的內容問題：外部 PDF、Office 文件與網頁資料在進入 Codex 前，缺少一致、可讀取與可保存的文字格式。
- 交付物：本機轉檔指令、使用說明、目前使用者帳號範圍的 Python 依賴。
- 完成的可驗證條件：對一個非機敏測試文件執行後，產生可讀取的 `.md`；原檔不被改動；輸出明確保存來源資訊。

## 已決定的方向

- 僅在本機轉換，不上傳文件到第三方服務。
- 優先使用 MarkItDown；掃描 PDF 與手寫內容不承諾辨識正確，轉檔後仍須人工抽查。
- 不轉換或提交私人家庭資料、帳密、未公開財務資料。

## 素材與版本

| 類型 | 路徑或來源 | 版本 | 狀態 |
| --- | --- | --- | --- |
| 轉檔工具 | `tools/markdown-intake/Convert-ToMarkdown.ps1` | v1 | 已驗證 |
| 使用說明 | `tools/markdown-intake/README.md` | v1 | 已完成 |

## 目前狀態

- 狀態：LOCKED。
- 已完成：安裝 MarkItDown 0.1.8 的 PDF、DOCX、PPTX、XLSX 解析依賴；以 `docs/PROJECT_CONTROL_TEMPLATE.md` 成功轉出 `tmp/markdown-intake/project-control-template.md` 並抽查內容。
- 阻塞或待確認：無。
- 下一個動作、主責與 Asia/Taipei 時點：下次收到外部研究資料時，先用此入口轉換並依對應 Skill 做查證與產出。
