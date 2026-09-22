# Markdown Intake

把外部資料轉成 Markdown，作為 Codex、查證與寫作流程的本機入口。它不會修改原檔，也不會把文件上傳到第三方服務。

## 一次性安裝

在 repo 根目錄執行。Windows 本機 Python 的隔離環境目前無法建立 `pip`，因此套件安裝在目前使用者帳號，不影響 repo 或系統管理員環境：

```powershell
py -m pip install --user -r tools/markdown-intake/requirements.txt
```

## 轉換

```powershell
pwsh -File tools/markdown-intake/Convert-ToMarkdown.ps1 `
  -InputPath 'D:\來源\研究報告.pdf' `
  -OutputPath 'tmp/markdown-intake/研究報告.md'
```

輸出檔已存在時，腳本會停止，避免蓋掉人工修訂。確認要重新產生才加上 `-Force`。

## 適用範圍與驗收

- 適用：PDF、DOCX、PPTX、XLSX、HTML、圖片與音訊等 MarkItDown 支援格式。
- 每次轉換後先抽查標題、表格、引用連結與前 2 段內容；掃描 PDF 與手寫資料應視為待人工 OCR 校對。
- 對外發布、事實查證與 SEO 寫作，仍要走對應 Skill 的來源驗證，不可把轉檔文字當成可信來源。
- 不要把私人家庭文件、憑證、未公開財務資料或可識別孩子資訊放進 repo；輸出預設放 `tmp/`，不納入 Git。
