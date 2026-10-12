# Monica API 本機串接

## 用途與邊界

`tools/monica-chat.ps1` 是本機的 Monica Chat Completions 封裝。它適合明確、可驗收、可外送的工作，例如批次摘要、翻譯、初稿變體與第二模型交叉檢查。

它不是 Codex 的主模型，也不會自動把整段工作對話送到 Monica。Codex 自訂模型供應商只支援 Responses API，Monica 文件目前提供的文字端點是 Chat Completions，因此不能直接替換本機 Codex 對話。

把文字送出前，先移除 API key、私人聯絡方式、未公開家庭資料、客戶資料與任何不必要的逐字稿原檔內容。Monica API 會將請求資料交由其服務與上游模型處理。

## 一次性設定（Windows）

1. 到 <https://platform.monica.im/api-keys> 建立 API Key，並確認 API Platform 帳戶另有可用餘額。
2. 在 repo 根目錄開啟 PowerShell，執行下面這個設定工具。它會以隱藏輸入方式接收 key，只寫入目前 Windows 使用者的環境變數。

```powershell
.\tools\setup-monica.ps1
```

3. 關閉並重新開啟 Codex。設定工具會讓目前 PowerShell 立即可用，但已經開啟的 Codex 程序要重開才會讀到新環境變數。

## 驗證

```powershell
.\tools\monica-chat.ps1 "只回覆：Monica 已連線。"
```

指定模型與讀原始回應：

```powershell
.\tools\monica-chat.ps1 -Model "gpt-4o" -Json "請用 JSON 回覆 {\"status\": \"ok\"}"
```

若出現餘額、認證或模型錯誤，請用 `-Json` 取得回應內容，再到 Monica API Platform 的 Billing、Usage 與 Models 頁面確認。Monica 訂閱 Advanced Credits 與 API Platform 餘額是分開計算的。

## 圖片生成

```powershell
.\tools\monica-image.ps1 -Provider flux -Model flux_dev -Size 768x1344 "暖白紙底的黑白水墨插圖。一名圓潤短髮眼鏡男性坐在書桌前思考。畫面不要文字。"
```

圖片會下載至 `tmp/monica/images/`，不會覆蓋既有檔案，也不會自動加入 Git。可用模型供應商為 `flux`、`dalle`、`sd`、`playground`、`ideogram`。每次建立圖片都會扣 API Platform 餘額，先用 1 張驗構圖，再決定是否批次產生。

## 圖片放大

```powershell
.\tools\monica-upscale.ps1 "https://可公開讀取的圖片網址.png"
```

這個端點目前只能使用 2 倍放大，輸入圖最大 `2048×2048`、輸出最大 `4096×4096`。它只接受圖片 URL，不能直接讀本機路徑。成功後會下載到 `tmp/monica/upscaled/`；不要拿私人家庭圖、未公開照片或需要保密的客戶素材當 URL 外送。

建議順序是：先用 `monica-image.ps1` 產生 1 張並核准構圖，再將回傳的 `source_url` 丟進 `monica-upscale.ps1`。這樣才不會把沒用的草圖逐張付費放大。

## 影片生成：目前不可串接

截至 2026-09-30，Monica Open API 的官方文件索引只列出 Chat、Image generation 與 Image tools，沒有任何 Video generation、建立任務或查詢任務狀態的 API。Monica 網頁／App 內能使用的影片功能，不能當成 API 可用功能。

因此目前不要把影片製作任務送到這個工具。若 Monica 日後發布影片 API 文件，至少要有模型名稱、建立端點、非同步任務查詢端點、輸出 URL 與計費規格，才接入正式影片流程。

## 在內容流程中的用法

先由 Codex 決定任務、刪除不該外送的資料，再把「要做什麼、輸入文字、期待格式」送給這個工具。回傳文字一律當草稿，仍須經事實、品牌與人工判斷驗收，不能當發布依據。
