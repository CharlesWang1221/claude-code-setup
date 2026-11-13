# Creator OS Mac Worker

這個程式是 Mac 的出站 Worker。它每 15 秒向 Creator OS 領一次工作，家中網路不需要 Port Forwarding。

## 安裝（只在 Mac 做）

1. 複製 `worker-config.example.json` 為 `worker-config.json`，填入正式 Worker URL、Mac 工作者 ID 與 Worker token。這個檔案含憑證，不可提交。
2. 只把已審核的 workflow 放進 `workflows`。LINE 傳入的自由文字不會變成 shell 指令。
3. 依實際使用者名稱修改 `.plist.example` 的 Node、repo 與 log 路徑，複製到 `~/Library/LaunchAgents/com.nonstandardanswer.creator-os-worker.plist`。
4. 執行 `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.nonstandardanswer.creator-os-worker.plist`。

停止時使用：`launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.nonstandardanswer.creator-os-worker.plist`。
