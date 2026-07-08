# 短影音自動剪輯 Pipeline

錄完影片，丟給 Claude Code 就出片。

## 快速開始

```powershell
# 1. 安裝環境
.\setup.ps1

# 2. 建立專案資料夾
$name = "我的短影音"
mkdir "..\..\video-projects\$name\01-raw"

# 3. 把錄影放進 01-raw/，然後開 Claude Code 說：
#    「剪這支 {影片名稱}」
```

## 工具清單

| 工具 | 功能 |
|------|------|
| `CLAUDE.md` | Claude Code 的完整 pipeline 指令 |
| `subtitle-editor.html` | 本地字幕微調編輯器（直接用瀏覽器開） |
| `scripts/transcribe.py` | Whisper 轉字幕 → SRT |
| `scripts/fetch_broll.py` | Pexels API 自動抓 B-roll |
| `scripts/compose.py` | FFmpeg 三區式 / 自拍風版型合成 |
| `setup.ps1` | 一鍵安裝所有依賴 |

## 資料夾結構

```
video-projects/
  {影片名稱}/
    01-raw/       ← 放原始錄影
    02-transcript/← SRT 字幕
    03-edited/    ← Auto-Editor 輸出
    04-broll/     ← Pexels B-roll
    05-render/    ← 最終成品
    06-publish/   ← 封面、文案
```

## 版型說明

**三區式**（預設，1080×1920 垂直）
- 上：標題 hook
- 中：主影片 + 字幕
- 下：CTA

**自拍風**
- 全螢幕影片
- 頂部半透明遮罩壓標題

## 字幕編輯器

用瀏覽器開啟 `subtitle-editor.html`：
- 拖曳 SRT 進去
- 直接修改文字
- 標記「大字」短語
- Ctrl+S 匯出 SRT，Ctrl+D 匯出大字 JSON

## 只保留 SRT

影片上傳後刪掉本機 MP4，只留 `02-transcript/*.srt`。
社群平台當雲端備份，SRT 就是你的製作紀錄。
