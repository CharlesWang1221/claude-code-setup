---
name: chibi-ink-illustrations
description: Create and edit consistent chibi ink-wash scene illustrations for 《不標準答案》 using the locked cast of Old Cha, Ah Fen, Da Bao, and Xiao Bao. Use whenever the user asks for character illustrations, scene art, story images, 「老查阿分大小寶做圖」, or revisions to these images.
---

# 角色水墨插圖

Use the built-in `imagegen` skill for all raster generation and editing.

## 角色鎖定

- 阿分：圓潤成年女性，黑色鮑伯頭、矩形眼鏡、白色 T 恤、深色長褲。
- 老查：圓潤成年男性，短黑髮、矩形眼鏡、白色 T 恤、深色長褲。
- 大寶：較年長女孩，及肩黑髮、連帽上衣、深色短裙。
- 小寶：較年幼女孩，長黑髮、彼得潘領連身裙。
- 固定畫風：3 頭身 Q 版、點點眼、圓潤四肢；手繪麥克筆質感、粗有機黑線、暖白紙底與柔灰墨暈。預設純黑白水墨；老查明確要求彩色時，改用低飽和彩色水墨，保留主導性的黑色墨線與紙張暈染。禁止寫實、3D、浮水印與模型生成中文。

## 視覺模式

- 未指定色彩時，使用黑白水墨。
- 明確要求「彩色版」或「彩色水墨」時，使用低飽和、透明疊染的彩墨，不可變成平塗卡通、賽璐璐、3D 或高飽和螢光色。
- 多角色家庭與桌遊場景的完整工作流程，讀 [references/podcast-cover-workflow.md](references/podcast-cover-workflow.md)。

## 私有設定與跨電腦使用

Before generating, resolve a private `chibi-ink-illustrations.config.json` file. Never commit the file, private source images, cloud-account names, or absolute paths.

1. Prefer a config beside the synced Google Drive output folder. On macOS, search `~/Library/CloudStorage` for the config; if exactly one is found, use it.
2. Otherwise use `.codex/chibi-ink-illustrations.local.json` at the repository root when present.
3. If no config is available, ask the user for the four reference images and final output folder, then create a private local config after approval.
4. Resolve relative paths from the config file's directory. `"final_output_dir": "."` means the config's directory.

Config schema:

```json
{
  "reference_images": {
    "ah_fen": "../三視圖/完成版/分.png",
    "old_cha": "../三視圖/完成版/查.png",
    "da_bao": "../三視圖/完成版/大寶.png",
    "xiao_bao": "../三視圖/完成版/小寶.png"
  },
  "final_output_dir": "."
}
```

## 工作流程

1. Identify the characters, action, emotion, props, setting, and requested aspect ratio from the user's scene.
2. Attach every character sheet for people appearing in the scene. State each person's name, gender/age cue, hair, clothing, action, and placement; do not infer these from names alone.
3. Generate one complete composition. Keep in-image copy, Chinese dialogue, and labels out of generation; reserve clean space or add them in post-production.
4. Inspect identity, costume, pose, scene hierarchy, and unwanted artifacts. If anything drifts, make one targeted edit only and explicitly say that all other elements must remain unchanged.
5. Preserve the original; move only the approved final PNG to `final_output_dir` with a descriptive non-overwriting name: `主題＿場景＿版本.png`.

## 編修規則

- Treat a request to change an existing image as an edit target. Preserve all stated invariants and alter only the named element.
- When removing speech bubbles, lightning, or dividers, request natural restoration of the background and do not leave blank cutouts.
- When text or a number must be exact, add it in post-production rather than trusting image generation.
