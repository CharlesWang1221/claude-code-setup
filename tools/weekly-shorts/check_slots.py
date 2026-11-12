#!/usr/bin/env python3
"""每週 6 支句剪的排程對帳表（2026-11-12 起，星期天建包前與讀回後都要跑）。

S4EP2 週（11/02）的漏洞：YouTube 少 2 支、IG 週五那支提前到週四跟週四撞日、FB 一支在 00:08 發出、
同一支三平台不同天發。規則早就寫了時段，但沒有機器擋，所以出錯也沒人發現。這支工具只讀檔、不碰平台。

用法：
  python tools/weekly-shorts/check_slots.py <weekly-plan.json>
      建包前：檢查 6 支的 target_at 是否落在母版時段、一天一支。
  python tools/weekly-shorts/check_slots.py <weekly-plan.json> --package <release-package.json>
      建包後：檢查授權包每列的時間與週計畫一致，四平台都有列。
  python tools/weekly-shorts/check_slots.py <weekly-plan.json> --readback
      排程讀回後與隔日巡檢：檢查 6 × 4 格每格都有平台讀回，讀回時間與 target_at 相同。

週計畫每支 item 的 platforms 讀回格式（星期天排程讀回後寫入）：
  "platforms": {"instagram": {"status": "SCHEDULED", "id": "...", "scheduled_at": "2026-11-10T20:30:00+08:00",
                              "readback_at": "2026-11-09T22:10:00+08:00"}, "facebook": {...}, "youtube": {...},
                "threads": {...}}
  status 可為 SCHEDULED／PUBLISHED／FAILED／BLOCKED／SUBMITTED_UNVERIFIED／MEDIA_MISSING／THUMBNAIL_FAILED。

例外：老查核准改時段或某平台不發時，在該 item 寫
  "slot_override": {"target_at": "...", "laocha_quote": "老查原話", "recorded_at": "..."}
  "platform_skip": {"youtube": "老查原話或原因"}
沒有老查原話的例外一律不算。

結束碼：0＝全部通過；1＝有錯，該列 BLOCKED，不得送授權包或標完成。
"""
import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

PLATFORMS = ('instagram', 'facebook', 'youtube', 'threads')
DAYS = ('mon', 'tue', 'wed', 'thu', 'fri', 'sat')
DEFAULT_SLOT = {d: ('12:00' if d == 'fri' else '20:30') for d in DAYS}  # docs/SHORT_VIDEO_WEEKLY_POLICY.md
OK_STATUS = {'SCHEDULED', 'PUBLISHED'}


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def parse(ts):
    if not ts or ts == 'immediate':
        return None
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        return None
    return dt if dt.utcoffset() == timedelta(hours=8) else None


def item_id(it):
    return it.get('id') or it.get('item_id')


def check_plan(plan, errs):
    items = plan.get('items') or []
    week_start = date.fromisoformat(plan['week_start'])
    if len(items) != 6:
        errs.append(f'週計畫有 {len(items)} 支，母版是 6 支')
    seen_dates = {}
    for it in items:
        iid = item_id(it) or '?'
        day = iid.split('-')[0]
        if day not in DAYS:
            errs.append(f'{iid}：id 不是 mon～sat 開頭，無法對時段')
            continue
        offset = DAYS.index(day)
        override = it.get('slot_override') or {}
        if override and not override.get('laocha_quote'):
            errs.append(f'{iid}：slot_override 沒有老查原話，不算例外')
            override = {}
        ts = override.get('target_at') or it.get('target_at')
        dt = parse(ts)
        if dt is None:
            errs.append(f'{iid}：target_at「{ts}」不是完整 +08:00 時間（immediate 也不行）')
            continue
        if not override:
            want_date = week_start + timedelta(days=offset)
            if dt.date() != want_date:
                errs.append(f'{iid}：日期 {dt.date()} 應為 {want_date}（{day}）')
            if dt.strftime('%H:%M') != DEFAULT_SLOT[day]:
                errs.append(f'{iid}：時間 {dt:%H:%M} 應為 {DEFAULT_SLOT[day]}')
        if dt.date() in seen_dates:
            errs.append(f'{iid}：與 {seen_dates[dt.date()]} 同一天（{dt.date()}），一天只能一支')
        seen_dates[dt.date()] = iid
    return {item_id(it): it for it in items}


def effective_target(it):
    return (it.get('slot_override') or {}).get('target_at') or it.get('target_at')


def check_package(by_id, pkg, errs):
    rows = pkg.get('items') if isinstance(pkg, dict) else pkg
    seen = {}
    for r in rows or []:
        iid = item_id(r)
        if iid not in by_id:
            continue  # 主題文、網站等非短片列不在本表
        want = parse(effective_target(by_id[iid]))
        got = parse(r.get('target_at'))
        if got is None or want is None or got != want:
            errs.append(f'{iid}：授權包時間「{r.get("target_at")}」與週計畫「{effective_target(by_id[iid])}」不同')
        plats = r.get('platforms') or ([r['platform']] if r.get('platform') else [])
        seen.setdefault(iid, set()).update(p.lower() for p in plats)
    for iid, it in by_id.items():
        skip = set((it.get('platform_skip') or {}).keys())
        missing = set(PLATFORMS) - seen.get(iid, set()) - skip
        if missing:
            errs.append(f'{iid}：授權包缺平台 {sorted(missing)}（要不發須在週計畫寫 platform_skip 與老查原話）')


def check_readback(by_id, errs):
    print('\n對帳表（○＝讀回相符、✕＝有問題、－＝老查核准不發）')
    print('item'.ljust(12) + ''.join(p[:2].upper().ljust(5) for p in PLATFORMS))
    for iid, it in by_id.items():
        want = parse(effective_target(it))
        skip = it.get('platform_skip') or {}
        cells = []
        for p in PLATFORMS:
            if p in skip:
                cells.append('－')
                continue
            rb = (it.get('platforms') or {}).get(p) or {}
            status = rb.get('status')
            got = parse(rb.get('scheduled_at'))
            problems = []
            if status not in OK_STATUS:
                problems.append(f'狀態 {status or "無讀回"}')
            if not rb.get('readback_at'):
                problems.append('沒有 readback_at')
            if got is None or got != want:
                problems.append(f'讀回時間 {rb.get("scheduled_at")} ≠ {effective_target(it)}')
            if problems:
                errs.append(f'{iid}／{p}：' + '、'.join(problems))
            cells.append('✕' if problems else '○')
        print(iid.ljust(12) + ''.join(c.ljust(4) for c in cells))


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')  # Windows 主控台預設 cp950，印不出 ✕
    ap =argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('plan')
    ap.add_argument('--package')
    ap.add_argument('--readback', action='store_true')
    a = ap.parse_args()
    errs = []
    by_id = check_plan(load(a.plan), errs)
    if a.package:
        check_package(by_id, load(a.package), errs)
    if a.readback:
        check_readback(by_id, errs)
    if errs:
        print('\nFAIL')
        for e in errs:
            print(' -', e)
        sys.exit(1)
    print('\nPASS')


if __name__ == '__main__':
    main()
