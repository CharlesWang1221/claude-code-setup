#!/usr/bin/env python3
"""句剪字幕校對 TXT 斷句檢查。

用法：python3 tools/caption-lines/check_caption_txt.py <字幕校對.txt>

TXT 格式（每支一段，cue 內一行＝畫面上一個字幕框）：
    【週一】
    1. 00:00:00,000 --> 00:00:03,280
    而且全家人那時候的
    ★其實很脆弱

規則來源：skills/podcast-teaser-video/SKILL.md「逐字字幕」。
FAIL 會讓結束碼為 1；WARN 只提示，交老查決定。
本工具不改檔、不重斷句，老查校對過的 TXT 一律原樣使用。
"""
import re
import sys
from pathlib import Path

MAX_WIDTH = 9.0  # 94 px 字級、安全框內寬 892 px：最多 9 個全形字
EMPH = '★'
BAD_HEAD = tuple('的了著過嗎呢吧啊呀喔哦嘛啦耶，。、！？,.!?；;：:）」』》')
BAD_TAIL = ('然後', '但是', '可是', '所以', '因為', '而且', '如果', '或是',
            '的', '跟', '和', '與', '把', '被', '讓', '給', '在', '對於', '一個', '這個', '那個',
            '《', '「', '『', '（')
SOLO_OK = {'對', '好', '嗯', '欸', '喔', '哦', '啊', '是', '沒', '不'}
CUE = re.compile(r'^\s*\d+\.\s*(\d\d:\d\d:\d\d[,.]\d{3})\s*-->\s*(\d\d:\d\d:\d\d[,.]\d{3})')
DAY = re.compile(r'^【(.+?)】')


def width(text):
    return sum(0.5 if ord(c) < 0x2E80 else 1.0 for c in text)


def main(path):
    day, cue, n_line, fails, warns = '?', None, 0, 0, 0
    emph = {}
    for no, raw in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        line = raw.strip()
        if m := DAY.match(line):
            day, cue = m.group(1), None
            continue
        if m := CUE.match(line):
            cue = line.split('.', 1)[0]
            continue
        if not line or cue is None:
            continue
        n_line += 1
        text = line[1:].strip() if line.startswith(EMPH) else line
        if line.startswith(EMPH):
            emph[day] = emph.get(day, 0) + 1
        where = f'L{no} {day} #{cue}「{text}」'
        problems = []
        if width(text) > MAX_WIDTH:
            problems.append(('FAIL', f'寬 {width(text):g} 字，超過 {MAX_WIDTH:g}；94 px 會被折成兩行'))
        if text.startswith(BAD_HEAD):
            problems.append(('FAIL', f'行首是「{text[0]}」，應黏回上一行'))
        tail = next((t for t in BAD_TAIL if text.endswith(t) and len(text) > len(t)), None)
        if tail:
            problems.append(('WARN', f'行尾掛「{tail}」，連接詞／虛詞通常移到下一行開頭'))
        if len(text) == 1 and text not in SOLO_OK:
            problems.append(('WARN', '單字成行，只允許獨立應答（對、好、嗯）'))
        for level, msg in problems:
            print(f'{level} {where}：{msg}')
            fails += level == 'FAIL'
            warns += level == 'WARN'
    for d, count in emph.items():
        if count > 2:
            print(f'WARN {d}：重點句（★）有 {count} 行，橘框太多會失去重點，建議 1–2 行')
            warns += 1
    print(f'共 {n_line} 行字幕：FAIL {fails}、WARN {warns}')
    return 1 if fails else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
