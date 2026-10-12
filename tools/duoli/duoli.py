#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多利（後勤管家）例行工作。只讀檔、不呼叫任何 AI 模型。

用法：
  python3 -I tools/duoli/duoli.py daily   [--dry-run] [--force]
  python3 -I tools/duoli/duoli.py weekly  [--dry-run] [--force]
  python3 -I tools/duoli/duoli.py ledger  [--dry-run] [--force]
  python3 -I tools/duoli/duoli.py auto        # 小查每日第一次回報前執行：只跑已到時間、且尚未跑過的工作
  python3 -I tools/duoli/duoli.py install     # （選用）安裝 macOS launchd 背景排程，需授權完整取用磁碟
  python3 -I tools/duoli/duoli.py uninstall

報告存在 output/weekly-shorts/duoli-reports/（已被 git 忽略）。當天或當週已跑過時，直接印出已存的報告。
寄信為選用（不進 repo）：token 存 macOS 鑰匙圈（服務 duoli-mailer、帳號 token），收件人寫在
~/.config/duoli/env 的 DUOLI_TO=...；缺任一項就不寄信。
"""
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

# Asia/Taipei 固定 UTC+8、無日光節約；不用 zoneinfo，Windows 才不需額外安裝 tzdata
TZ = dt.timezone(dt.timedelta(hours=8), "Asia/Taipei")
REPO = Path(__file__).resolve().parents[2]
STATE = REPO / "output" / "weekly-shorts" / "duoli-reports"
CONFIG = Path.home() / ".config" / "duoli" / "env"
MAILER_URL = "https://duoli-mailer.siming1221.workers.dev"
EVIDENCE = REPO / "docs" / "RELEASE_EVIDENCE_REGISTER.md"
WEEKLY_DIR = REPO / "output" / "weekly-shorts"
TEMPLATE = REPO / "docs" / "templates" / "weekly-plan.template.json"
LAUNCHD_LABEL = "com.beyondans.duoli"
LAUNCHD_TEMPLATE = Path(__file__).resolve().parent / "launchd" / "com.beyondans.duoli.plist.template"
DISK_WARN_GB = 30
STALE_DAYS = 30
DATE_RE = re.compile(r"(20\d{2})-(\d{2})-(\d{2})(?:\s+(\d{1,2}):(\d{2}))?")
PATH_RE = re.compile(r"`((?:output|video-projects)/[^`]+?\.mp4)`")


def now():
    return dt.datetime.now(TZ)


def monday_of(d):
    return d - dt.timedelta(days=d.weekday())


# ---------- 讀取發布證據庫 ----------

def evidence_rows():
    if not EVIDENCE.exists():
        return []
    rows = []
    for line in EVIDENCE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| ---") or line.startswith("| 資產 ID"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        m = DATE_RE.search(cells[5])
        when = None
        if m:
            y, mo, d, hh, mm = m.groups()
            when = dt.datetime(int(y), int(mo), int(d), int(hh or 0), int(mm or 0), tzinfo=TZ)
        rows.append({
            "id": cells[0].strip("`"),
            "platform": cells[1],
            "version": cells[2],
            "status": cells[3].strip("`"),
            "when": when,
            "has_time": bool(m and m.group(4)),
        })
    return rows


def is_published(status):
    return "已公開" in status


def is_pending(status):
    return not is_published(status) and "跳過" not in status


# ---------- 每日檢查 ----------

def section_schedule(t):
    today = t.date()
    tomorrow = today + dt.timedelta(days=1)
    upcoming, overdue = [], []
    for r in evidence_rows():
        if not r["when"]:
            continue
        d = r["when"].date()
        passed = r["when"] < t if r["has_time"] else d < today
        if passed and "已排程" in r["status"] and (today - d).days <= 14:
            overdue.append(r)
        elif not passed and d in (today, tomorrow) and is_pending(r["status"]):
            upcoming.append(r)
    lines = []
    if upcoming:
        lines.append("今明兩天要發布：")
        for r in sorted(upcoming, key=lambda x: x["when"]):
            hm = r["when"].strftime("%m/%d %H:%M") if r["has_time"] else r["when"].strftime("%m/%d")
            lines.append("- %s｜%s｜%s｜狀態 %s" % (hm, r["id"], r["platform"], r["status"]))
    else:
        lines.append("今明兩天沒有排定發布。")
    if overdue:
        lines.append("已過預定時間、證據庫仍是「已排程」（需讀回公開證據）：")
        for r in overdue:
            lines.append("- %s｜%s｜預定 %s" % (r["id"], r["platform"], r["when"].strftime("%m/%d %H:%M")))
    return "排程看門（星期天）", lines, bool(overdue)


def section_skill_health():
    if os.name == "nt":
        script = REPO / "tools" / "check-skill-authority.ps1"
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]
    else:
        script = REPO / "tools" / "check-skill-authority.sh"
        cmd = ["bash", str(script)]
    if not script.exists():
        return "Skill 健康（師傅）", ["找不到來源檢查腳本：%s" % script.name], True
    try:
        p = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError as e:
        return "Skill 健康（師傅）", ["無法執行來源檢查：%s" % e], True
    out = (p.stdout + p.stderr).strip().splitlines()
    bad = [l for l in out if l.startswith(("DIFF", "MISSING", "FAIL", "RED"))]
    if p.returncode == 0 and not bad:
        return "Skill 健康（師傅）", ["PASS"], False
    return "Skill 健康（師傅）", ["FAIL（exit %d）" % p.returncode] + ["- " + l for l in (bad or out[-5:])], True


def section_files(t):
    lines, alert = [], False
    # 1. 待發布的檔案是否存在、同資料夾是否有多個 MP4
    seen = set()
    for r in evidence_rows():
        if not is_pending(r["status"]) or not r["when"] or r["when"].date() < t.date() - dt.timedelta(days=1):
            continue
        for rel in PATH_RE.findall(r["version"]):
            if rel in seen:
                continue
            seen.add(rel)
            f = REPO / rel
            if not f.exists():
                lines.append("- 找不到待發布檔案：%s（%s）" % (rel, r["id"]))
                alert = True
                continue
            mp4s = sorted(x.name for x in f.parent.glob("*.mp4"))
            if len(mp4s) > 1:
                lines.append("- %s 同資料夾有 %d 個 MP4，上傳前確認只用 %s：%s" % (r["id"], len(mp4s), f.name, "、".join(mp4s)))
                alert = True
    # 2. 本週產線資料夾（lane_dir）多個 MP4
    plan = WEEKLY_DIR / monday_of(t.date()).isoformat() / "weekly-plan.json"
    if plan.exists():
        try:
            items = json.loads(plan.read_text(encoding="utf-8")).get("items", [])
        except ValueError:
            items = []
            lines.append("- 本週週計畫 JSON 無法解析：%s" % plan.relative_to(REPO))
            alert = True
        for it in items:
            lane = it.get("lane_dir")
            if lane and (REPO / lane).is_dir():
                mp4s = list((REPO / lane).glob("*.mp4"))
                if len(mp4s) > 1:
                    lines.append("- %s 的產線資料夾有 %d 個 MP4" % (it.get("id"), len(mp4s)))
                    alert = True
    # 3. 過期渲染檔（只回報，不刪除）
    cutoff = t.timestamp() - STALE_DAYS * 86400
    stale_bytes, stale_n = 0, 0
    for base in (REPO / "output", REPO / "video-projects"):
        if base.is_dir():
            for f in base.rglob("*.mp4"):
                try:
                    st = f.stat()
                except OSError:
                    continue
                if st.st_mtime < cutoff:
                    stale_bytes += st.st_size
                    stale_n += 1
    if stale_n:
        lines.append("- 超過 %d 天未動的 MP4：%d 個，共 %.1f GB（只回報，不自動刪除）" % (STALE_DAYS, stale_n, stale_bytes / 1e9))
    # 4. 鐵雄閘門緊急放行紀錄（近 7 天）
    olog = WEEKLY_DIR / "qa-overrides.log"
    if olog.exists():
        recent = []
        for line in olog.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) >= 4:
                try:
                    when = dt.datetime.fromisoformat(parts[0])
                except ValueError:
                    continue
                if (t - when).days < 7:
                    recent.append("- %s｜%s｜理由：%s" % (when.strftime("%m/%d %H:%M"), parts[1], parts[3]))
        if recent:
            lines.append("近 7 天鐵雄閘門緊急放行（需確認任務卡已記錄老查的決定）：")
            lines.extend(recent)
            alert = True
    # 5. 磁碟空間
    free_gb = shutil.disk_usage(str(REPO)).free / 1e9
    if free_gb < DISK_WARN_GB:
        lines.append("- 磁碟剩餘 %.0f GB，低於 %d GB" % (free_gb, DISK_WARN_GB))
        alert = True
    else:
        lines.append("- 磁碟剩餘 %.0f GB" % free_gb)
    return "檔案巡邏（廠長、鐵雄）", lines, alert


def build_daily(t):
    sections = [section_schedule(t), section_skill_health(), section_files(t)]
    alert = any(s[2] for s in sections)
    title = "多利｜每日巡檢 %s%s" % (t.strftime("%m/%d"), "｜有異常" if alert else "｜無異常")
    return title, sections


# ---------- 每週一：開週計畫、列復盤 ----------

def build_weekly(t, dry_run):
    week = monday_of(t.date())
    plan_dir = WEEKLY_DIR / week.isoformat()
    plan = plan_dir / "weekly-plan.json"
    lines = []
    if plan.exists():
        lines.append("本週週計畫已存在，跳過：%s" % plan.relative_to(REPO))
    else:
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        data["week_start"] = week.isoformat()
        if not dry_run:
            plan_dir.mkdir(parents=True, exist_ok=True)
            with open(plan, "x", encoding="utf-8") as fh:  # 已存在就失敗，絕不覆蓋
                fh.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        lines.append("%s本週週計畫空殼：%s" % ("（試跑）將建立" if dry_run else "已建立", plan.relative_to(REPO)))
    due = []
    week_end = week + dt.timedelta(days=6)
    for r in evidence_rows():
        if not r["when"]:
            continue
        inferred = "已排程" in r["status"] and r["when"] < t
        if not (is_published(r["status"]) or inferred):
            continue
        for n in (7, 30):
            d = r["when"].date() + dt.timedelta(days=n)
            if week <= d <= week_end:
                due.append("- 第 %d 天復盤 %s：%s（%s）%s" % (n, d.strftime("%m/%d"), r["id"], r["platform"],
                                                        "（依排程時間推定已公開）" if inferred else ""))
    if due:
        lines.append("本週到期的復盤（成析）：")
        lines.extend(due)
    else:
        lines.append("本週沒有到期的復盤。")
    intel = plan_dir / "intel-report.md"
    if intel.exists():
        lines.append("本週選題情報週報已完成：%s" % intel.relative_to(REPO))
    else:
        lines.append("提醒：本週選題情報週報尚未執行。請小查用 Codex 手動跑一次（預算卡 S），存到 %s，交小渡、小市。"
                     % intel.relative_to(REPO))
    title = "多利｜週計畫開檔 %s" % week.strftime("%m/%d")
    return title, [("週計畫與復盤（阿派、成析）", lines, False)]


# ---------- 每週日：帳本原始數字 ----------

REDO_RE = re.compile(r"重做次數\s*[:：]\s*(\d+)")
CREDIT_RE = re.compile(r"付費點數\s*[:：]\s*(.+)")


def ledger_week(t):
    sunday_2000 = lambda wk: dt.datetime.combine(wk + dt.timedelta(days=6), dt.time(20, 0), TZ)
    week = monday_of(t.date())
    return week if t >= sunday_2000(week) else week - dt.timedelta(days=7)


def build_ledger(t):
    week = ledger_week(t)
    plan = WEEKLY_DIR / week.isoformat() / "weekly-plan.json"
    lines = []
    if not plan.exists():
        lines.append("找不到 %s 那週的週計畫，無法統計。" % week.isoformat())
    else:
        items = json.loads(plan.read_text(encoding="utf-8")).get("items", [])
        total, missing = 0, []
        for it in items:
            lane = it.get("lane_dir")
            hf = (REPO / lane / "handoff.md") if lane else None
            if not hf or not hf.exists():
                missing.append(it.get("id"))
                continue
            text = hf.read_text(encoding="utf-8")
            m = REDO_RE.search(text)
            redo = int(m.group(1)) if m else None
            credits = CREDIT_RE.search(text)
            total += redo or 0
            flag = "（重做滿 2 次）" if redo is not None and redo >= 2 else ""
            lines.append("- %s｜預算 %s｜重做 %s%s｜付費點數 %s" % (
                it.get("id"), it.get("budget") or "未填", "未填" if redo is None else redo, flag,
                credits.group(1).strip() if credits else "未填"))
        lines.insert(0, "週次 %s：交件包重做次數合計 %d" % (week.isoformat(), total))
        if missing:
            lines.append("沒有交件包可統計：%s" % "、".join(str(x) for x in missing))
    lines.append("以上是原始數字，判斷與結算由省長負責。")
    title = "多利｜帳本原始數字 %s 週" % week.strftime("%m/%d")
    return title, [("交給省長", lines, False)], week


# ---------- 輸出：存檔、通知、寄信 ----------

def render_text(title, sections):
    out = [title, ""]
    for name, lines, alert in sections:
        out.append("【%s】%s" % (name, "⚠" if alert else ""))
        out.extend(lines)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_html(title, sections):
    parts = ["<h2>%s</h2>" % html.escape(title)]
    for name, lines, alert in sections:
        parts.append("<h3>%s%s</h3>" % (html.escape(name), "（有異常）" if alert else ""))
        parts.append("<pre style='font-family:inherit;white-space:pre-wrap'>%s</pre>" % html.escape("\n".join(lines)))
    parts.append("<p style='color:#888'>多利自動巡檢，不使用 AI 額度。</p>")
    return "\n".join(parts)


def read_config():
    cfg = {}
    if CONFIG.exists():
        for line in CONFIG.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"')
    return cfg


def read_token():
    try:
        p = subprocess.run(["security", "find-generic-password", "-s", "duoli-mailer", "-a", "token", "-w"],
                           capture_output=True, text=True)
    except OSError:  # Windows 沒有 macOS 鑰匙圈
        return ""
    return p.stdout.strip() if p.returncode == 0 else ""


def send_mail(title, sections):
    to = read_config().get("DUOLI_TO", "")
    token = read_token()
    if not to or not token:
        return False, "未設定收件人或 token，略過寄信"
    body = json.dumps({"to": to, "subject": title[:160], "html": render_html(title, sections)}).encode("utf-8")
    req = urllib.request.Request(MAILER_URL, data=body, method="POST", headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return 200 <= resp.status < 300, "寄信 HTTP %d" % resp.status
    except Exception as e:  # noqa: BLE001 寄信失敗不影響存檔
        return False, "寄信失敗：%s" % e


def notify(title, msg):
    script = 'display notification %s with title %s' % (json.dumps(msg), json.dumps(title))
    subprocess.run(["osascript", "-e", script], capture_output=True)


def deliver(kind, key, title, sections, dry_run):
    text = render_text(title, sections)
    print(text)
    if dry_run:
        print("（試跑：不存檔、不寄信、不通知）")
        return
    ok, msg = send_mail(title, sections)
    if not ok and os.environ.get("XPC_SERVICE_NAME") == LAUNCHD_LABEL:
        notify("多利", title.replace("多利｜", ""))  # 只有背景排程才跳通知
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        (STATE / ("%s-%s.md" % (kind, key))).write_text(text, encoding="utf-8")
        (STATE / ("done-%s-%s" % (kind, key))).write_text("%s\n%s\n" % (now().isoformat(), msg), encoding="utf-8")
    except OSError as e:
        msg += "；報告未能存檔：%s" % e
    print(msg)


def done(kind, key):
    return (STATE / ("done-%s-%s" % (kind, key))).exists()


def show_saved(kind, key, label):
    f = STATE / ("%s-%s.md" % (kind, key))
    print("%s已完成，以下是已存的報告：\n" % label)
    print(f.read_text(encoding="utf-8") if f.exists() else "（找不到報告檔）")


# ---------- 指令 ----------

def run_daily(t, dry_run, force):
    key = t.date().isoformat()
    if done("daily", key) and not force and not dry_run:
        show_saved("daily", key, "今日巡檢")
        return
    title, sections = build_daily(t)
    deliver("daily", key, title, sections, dry_run)


def run_weekly(t, dry_run, force):
    key = monday_of(t.date()).isoformat()
    if done("weekly", key) and not force and not dry_run:
        show_saved("weekly", key, "本週開檔")
        return
    title, sections = build_weekly(t, dry_run)
    deliver("weekly", key, title, sections, dry_run)


def run_ledger(t, dry_run, force):
    title, sections, week = build_ledger(t)
    key = week.isoformat()
    if done("ledger", key) and not force and not dry_run:
        show_saved("ledger", key, "該週帳本")
        return
    deliver("ledger", key, title, sections, dry_run)


def run_auto(t):
    at_0730 = t.time() >= dt.time(7, 30)
    if at_0730:
        run_weekly(t, False, False)  # 週一 07:30 起；週間開機也會補跑一次
        run_daily(t, False, False)
    week = ledger_week(t)
    plan_exists = (WEEKLY_DIR / week.isoformat() / "weekly-plan.json").exists()
    if plan_exists and not done("ledger", week.isoformat()) and (t.date() - week).days >= 6:
        run_ledger(t, False, False)


def install():
    target = Path.home() / "Library" / "LaunchAgents" / (LAUNCHD_LABEL + ".plist")
    plist = LAUNCHD_TEMPLATE.read_text(encoding="utf-8")
    plist = plist.replace("{{PYTHON}}", shutil.which("python3") or "/usr/bin/python3")
    plist = plist.replace("{{SCRIPT}}", str(Path(__file__).resolve()))
    plist = plist.replace("{{LOG}}", str(STATE / "launchd.log"))
    STATE.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    uid = str(os.getuid())
    subprocess.run(["launchctl", "bootout", "gui/%s/%s" % (uid, LAUNCHD_LABEL)], capture_output=True)
    target.write_text(plist, encoding="utf-8")
    p = subprocess.run(["launchctl", "bootstrap", "gui/" + uid, str(target)], capture_output=True, text=True)
    print("已安裝：%s（%s）" % (target, "OK" if p.returncode == 0 else p.stderr.strip()))


def uninstall():
    target = Path.home() / "Library" / "LaunchAgents" / (LAUNCHD_LABEL + ".plist")
    subprocess.run(["launchctl", "bootout", "gui/%s/%s" % (os.getuid(), LAUNCHD_LABEL)], capture_output=True)
    if target.exists():
        target.unlink()
    print("已移除 launchd 排程。報告保留在 %s" % STATE)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, flags = argv[0], set(argv[1:])
    dry, force, t = "--dry-run" in flags, "--force" in flags, now()
    if cmd == "daily":
        run_daily(t, dry, force)
    elif cmd == "weekly":
        run_weekly(t, dry, force)
    elif cmd == "ledger":
        run_ledger(t, dry, force)
    elif cmd == "auto":
        run_auto(t)
    elif cmd == "install":
        install()
    elif cmd == "uninstall":
        uninstall()
    else:
        print("未知指令：%s" % cmd)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
