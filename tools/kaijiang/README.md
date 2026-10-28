# 嘴型元件（開講試點）

把角色前視圖＋一段原音做成會說話的水墨頭像，輸出開講直式（9:16）與油管角落（16:9）兩種試片。全程本機運算，$0。任務脈絡見 `video-projects/kaijiang-pilot/BRIEF.md`。

## 需要的東西

- Python 3＋`pillow numpy pypinyin`（建議放 venv）
- 逐字時間碼：openai-whisper `small`，`word_timestamps=True`，輸出 `[{"w","s","e"}]` 的 `words.json`
- ffmpeg／ffprobe
- 角色前視圖：私有三視圖，不進 repo

## 執行

```bash
python engine.py <本目錄> <角色三視圖.png> words.json clip.wav clip.m4a <中文字型.ttf> <輸出前綴>
python mouths.py <角色三視圖.png> <聯絡表.png> <中文字型.ttf>   # 只出 6 種嘴型聯絡表
```

- `clip.wav`：16 kHz 單聲道，算音量包絡；`clip.m4a`：成片音軌。
- 輸出 `<前綴>-big-9x16.mp4` 與 `<前綴>-small-16x9.mp4`；`STILL=1` 只出手臂測試圖。

## 目前狀態（v7）

- 座標是老查三視圖（2400 × 1760）的實測值：嘴心 (490, 604)、眼睛 (400, 484)／(562, 484)。換阿分要重量座標。
- 6 種嘴型（閉、抿、小開、大開、扁、圓）全由程式重畫，線寬固定 8 px；嘴型由 `pypinyin` 韻母判斷。
- 動作：重音點頭、疑問詞歪頭、隨機眨眼、呼吸。
- 手臂切層擺動已停用（`arm_angle` 回傳 0）：原圖手臂貼身體，切開會破圖。手勢改走姿勢圖（階段 2）。
- 去背用 flood fill 挖亮色紙底；輪廓線有缺口的圖會漏挖，換圖要逐張檢查。
