# 本機 Flow 連線

使用 `gflow-cli==0.79.1` 的 `gflow video i2v`。這是非官方、MIT 授權的本機 Chrome 自動化工具；它操作使用者自己的 Flow 網頁帳號並消耗既有訂閱點數，不經 useapi.net。來源：[gflow-cli](https://github.com/ffroliva/gflow-cli)、[PyPI 0.79.1](https://pypi.org/project/gflow-cli/0.79.1/)。

## 一次性安裝

macOS 需要 Python 3.11 以上及 Google Chrome。將環境放在 repo 的 `.flow-tools/`（已列入 `.gitignore`）：

```bash
python3.11 -m venv .flow-tools/gflow-venv
.flow-tools/gflow-venv/bin/python -m pip install 'gflow-cli==0.79.1'
export GFLOW_BIN="$PWD/.flow-tools/gflow-venv/bin/gflow"
"$GFLOW_BIN" --version
```

先以 `command -v python3.11` 查詢本機 Python；不要沿用另一台電腦的絕對路徑。若執行時提示缺 Playwright Chromium，使用同一環境執行 `.flow-tools/gflow-venv/bin/python -m playwright install chromium`。登入用 `"$GFLOW_BIN" auth login --browser chrome`，由老查在開啟的 Chrome 視窗完成；用 `"$GFLOW_BIN" auth status` 驗證。新版 `flow.google.com` 帳號可能無法透過 `gflow credits user` 讀取點數，直接在 Flow 網頁的帳戶選單查看。不要將 browser profile 或 cookies 複製進 repo，也不要用 `useapi.net` 的遠端 cookie 託管代替此流程。

Windows PC 可用 Python 3.11 以上建立 `.flow-tools\gflow-venv`；在 PowerShell 執行 `python -m venv .flow-tools\gflow-venv`，然後 `& .flow-tools\gflow-venv\Scripts\python.exe -m pip install gflow-cli==0.79.1`，再以同目錄的 `gflow.exe` 執行登入。Flow 工具屬機器本機授權，換電腦需重新登入。

## 帳號與成本

- 不要求老查交出 Google 密碼、cookies、API key 或 Flow Session。只需老查在本機 Chrome 登入 Google Flow。
- `gflow-cli` 的 `i2v` 模型支援 `omni-flash`、`veo-lite`、`veo-fast`、`veo-quality`。每次輸出數量固定 1；點數及模型可用性可能改變，生成前以 Flow 介面確認。
- 本 Skill 的腳本在執行前寫入 `.flow-run.json`，同一輸出不可重送。若 CLI 已在 Flow 提交但本機下載失敗，優先回收原成品，避免重扣點。
- 本地 `FFmpeg` 只做檢查和音畫合成。1080 × 1920 輸出尺寸不代表來源生成片有相同原生解析度。

PC 更新 Skill 不會同步 Chrome 登入、Flow 訂閱狀態或私有素材。Windows 安裝及登入由該機器本機完成；本次只在 Mac 實測生成與 UI 回收，Windows 真正產片仍須單支驗證。
