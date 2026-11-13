"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { compareEpisodes, CSV_COLUMNS, PRIMARY_METRIC_LABEL, TRAFFIC_PLATFORMS, TRAFFIC_WINDOWS, type TrafficPlatform, type TrafficRow, type TrafficWindow } from "@/lib/traffic";
import { commitTrafficCsv, loadTraffic, previewTrafficCsv, saveTraffic, type ImportSummary, type TrafficRole } from "@/lib/traffic-api";
import styles from "./traffic.module.css";

type FormState = {
  episode: string;
  contentLabel: string;
  platform: TrafficPlatform;
  window: TrafficWindow;
  primaryValue: string;
  reach: string;
  engagements: string;
  linkClicks: string;
  followerDelta: string;
  note: string;
};

const emptyForm: FormState = { episode: "", contentLabel: "", platform: "Firstory", window: "D7", primaryValue: "", reach: "", engagements: "", linkClicks: "", followerDelta: "", note: "" };

const numberFormat = new Intl.NumberFormat("zh-TW");
const formatCount = (value: number | null) => (value === null ? "—" : numberFormat.format(value));
const formatDelta = (value: number | null) => (value === null ? "—" : `${value > 0 ? "+" : ""}${numberFormat.format(value)}`);

export default function TrafficView() {
  const [rows, setRows] = useState<TrafficRow[]>([]);
  const [role, setRole] = useState<TrafficRole>("viewer");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [episode, setEpisode] = useState("");
  const [form, setForm] = useState<FormState>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [csvText, setCsvText] = useState("");
  const [preview, setPreview] = useState<ImportSummary | null>(null);

  const episodes = useMemo(() => [...new Set(rows.map((row) => row.episode))].sort(compareEpisodes).reverse(), [rows]);
  const activeEpisode = episode || episodes[0] || "";
  const previousEpisode = episodes[episodes.indexOf(activeEpisode) + 1] ?? "";
  const canEdit = role === "owner" || role === "editor";

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await loadTraffic();
      setRows(data.rows);
      setRole(data.role);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "讀取失敗。");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => void refresh(), 0);
    return () => window.clearTimeout(timer);
  }, [refresh]);

  function find(target: string, platform: TrafficPlatform, obs: TrafficWindow) {
    return rows.find((row) => row.episode === target && row.contentLabel === "" && row.platform === platform && row.window === obs);
  }

  const detailRows = rows
    .filter((row) => row.episode === activeEpisode)
    .sort((a, b) => a.contentLabel.localeCompare(b.contentLabel) || TRAFFIC_PLATFORMS.indexOf(a.platform) - TRAFFIC_PLATFORMS.indexOf(b.platform) || TRAFFIC_WINDOWS.indexOf(a.window) - TRAFFIC_WINDOWS.indexOf(b.window));

  async function submitForm(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");
    const blankToNull = (value: string) => (value.trim() === "" ? null : value);
    try {
      const result = await saveTraffic({
        ...form,
        primaryValue: form.primaryValue,
        reach: blankToNull(form.reach),
        engagements: blankToNull(form.engagements),
        linkClicks: blankToNull(form.linkClicks),
        followerDelta: blankToNull(form.followerDelta),
      });
      setRows(result.rows);
      setEpisode(form.episode.trim().toUpperCase());
      setNotice(`已儲存 ${form.episode.trim().toUpperCase()} · ${form.platform} · ${form.window}`);
      setForm((current) => ({ ...emptyForm, episode: current.episode, contentLabel: current.contentLabel, window: current.window }));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "儲存失敗。");
    } finally {
      setSaving(false);
    }
  }

  async function readFile(file: File | undefined) {
    if (!file) return;
    setCsvText(await file.text());
    setPreview(null);
  }

  async function runPreview() {
    setError("");
    setNotice("");
    try {
      setPreview(await previewTrafficCsv(csvText));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "預覽失敗。");
    }
  }

  async function runCommit() {
    setError("");
    try {
      const result = await commitTrafficCsv(csvText);
      setRows(result.rows);
      setNotice(`已匯入 ${result.imported} 列（其中覆寫 ${result.overwrites} 列）。`);
      setPreview(null);
      setCsvText("");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "匯入失敗。");
    }
  }

  const update = (field: keyof FormState) => (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setForm((current) => ({ ...current, [field]: event.target.value }));

  return <main className={styles.page}>
    <header className={styles.header}>
      <div>
        <Link href="/" className={styles.back}>← 回工作站</Link>
        <p className="eyebrow">TRAFFIC LEDGER · 第一階段手填＋CSV</p>
        <h1>總流量</h1>
        <p className={styles.lead}>每個平台各算各的。Firstory 下載和 IG 觀看不是同一種東西，這裡不把它們加成一個大數字。</p>
      </div>
      <div className={styles.headerActions}>
        <label className={styles.episodePicker}>集數
          <select value={activeEpisode} onChange={(event) => setEpisode(event.target.value)} disabled={!episodes.length}>
            {!episodes.length && <option value="">尚無資料</option>}
            {episodes.map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
        <button className="ghost-button" onClick={() => void refresh()} disabled={loading}>{loading ? "讀取中…" : "重新讀取"}</button>
      </div>
    </header>

    {error && <p className={`${styles.message} ${styles.error}`} role="alert">{error}</p>}
    {notice && <p className={styles.message} role="status">{notice}</p>}
    {!canEdit && !loading && !error && <p className={styles.message}>你目前是檢視權限，只能讀，不能填寫或匯入。</p>}

    <section aria-label="各平台 D7">
      <p className="eyebrow">D7 · {activeEpisode || "—"} 對比 {previousEpisode || "（無上一集資料）"}</p>
      <div className={styles.cards}>
        {TRAFFIC_PLATFORMS.map((platform) => {
          const current = find(activeEpisode, platform, "D7");
          const previous = previousEpisode ? find(previousEpisode, platform, "D7") : undefined;
          const change = current && previous && previous.primaryValue > 0 ? Math.round(((current.primaryValue - previous.primaryValue) / previous.primaryValue) * 100) : null;
          return <article className={styles.card} key={platform}>
            <span className={styles.cardPlatform}>{platform}</span>
            <strong className={current ? "" : styles.empty}>{current ? formatCount(current.primaryValue) : "未填"}</strong>
            <small>{PRIMARY_METRIC_LABEL[platform]}</small>
            <span className={change === null ? styles.flat : change >= 0 ? styles.up : styles.down}>
              {change === null ? (previous ? `上一集 ${formatCount(previous.primaryValue)}` : "無上一集可比") : `${change >= 0 ? "▲" : "▼"} ${Math.abs(change)}%（上一集 ${formatCount(previous!.primaryValue)}）`}
            </span>
          </article>;
        })}
      </div>
    </section>

    <section className="panel">
      <div className="panel-heading"><div><p className="eyebrow">DETAIL</p><h2>{activeEpisode || "尚未選擇集數"} 明細</h2></div><span className="badge">{detailRows.length} 列</span></div>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead><tr><th>內容</th><th>平台</th><th>觀察窗</th><th>主要數字</th><th>觸及／曝光</th><th>互動</th><th>導流點擊</th><th>追蹤變化</th><th>來源</th><th>填寫人</th><th>備註</th></tr></thead>
          <tbody>
            {detailRows.map((row) => <tr key={row.id}>
              <td>{row.contentLabel || "集數本身"}</td>
              <td>{row.platform}</td>
              <td>{row.window}</td>
              <td className={styles.num}>{formatCount(row.primaryValue)} <small>{PRIMARY_METRIC_LABEL[row.platform]}</small></td>
              <td className={styles.num}>{formatCount(row.reach)}</td>
              <td className={styles.num}>{formatCount(row.engagements)}</td>
              <td className={styles.num}>{formatCount(row.linkClicks)}</td>
              <td className={styles.num}>{formatDelta(row.followerDelta)}</td>
              <td>{row.source}</td>
              <td>{row.enteredBy}</td>
              <td>{row.note}</td>
            </tr>)}
            {!detailRows.length && <tr><td colSpan={11} className={styles.emptyRow}>{loading ? "讀取中…" : "這一集還沒有資料。"}</td></tr>}
          </tbody>
        </table>
      </div>
    </section>

    {canEdit && <div className={styles.editors}>
      <form className="panel" onSubmit={submitForm}>
        <p className="eyebrow">MANUAL ENTRY</p>
        <h2>手填一列</h2>
        <p className={styles.hint}>同集數、同內容、同平台、同觀察窗再填一次，會覆寫舊值。</p>
        <div className={styles.formGrid}>
          <label>集數<input required placeholder="S4EP4" value={form.episode} onChange={update("episode")} /></label>
          <label>內容（留空＝集數本身）<input placeholder="例：週二句剪" value={form.contentLabel} onChange={update("contentLabel")} /></label>
          <label>平台<select value={form.platform} onChange={update("platform")}>{TRAFFIC_PLATFORMS.map((item) => <option key={item}>{item}</option>)}</select></label>
          <label>觀察窗<select value={form.window} onChange={update("window")}>{TRAFFIC_WINDOWS.map((item) => <option key={item}>{item}</option>)}</select></label>
          <label>主要數字（{PRIMARY_METRIC_LABEL[form.platform]}）<input required inputMode="numeric" value={form.primaryValue} onChange={update("primaryValue")} /></label>
          <label>觸及／曝光<input inputMode="numeric" value={form.reach} onChange={update("reach")} /></label>
          <label>互動數<input inputMode="numeric" value={form.engagements} onChange={update("engagements")} /></label>
          <label>導流點擊<input inputMode="numeric" value={form.linkClicks} onChange={update("linkClicks")} /></label>
          <label>追蹤數變化<input inputMode="numeric" placeholder="可為負數" value={form.followerDelta} onChange={update("followerDelta")} /></label>
          <label className={styles.wide}>備註<input placeholder="Firstory 請註明 UTC+0" value={form.note} onChange={update("note")} /></label>
        </div>
        <button className="primary-button full" disabled={saving}>{saving ? "儲存中…" : "儲存這一列"}</button>
      </form>

      <section className="panel">
        <p className="eyebrow">CSV IMPORT</p>
        <h2>CSV 匯入</h2>
        <p className={styles.hint}>欄位：<code>{CSV_COLUMNS.join(",")}</code>。範本在 <code>apps/creator-os/docs/traffic-csv-template.csv</code>。先預覽，沒有錯誤列才能寫入。</p>
        <input type="file" accept=".csv,text/csv" onChange={(event) => void readFile(event.target.files?.[0])} />
        <textarea className={styles.csv} placeholder="也可以直接貼上 CSV 內容" value={csvText} onChange={(event) => { setCsvText(event.target.value); setPreview(null); }} />
        <button className="ghost-button full" onClick={() => void runPreview()} disabled={!csvText.trim()}>預覽</button>
        {preview && <div className={styles.preview}>
          <p>可匯入 {preview.total} 列：新增 {preview.inserts}、覆寫 {preview.overwrites}。錯誤 {preview.errors.length} 列。</p>
          {preview.errors.length > 0 && <ul className={styles.errorList}>{preview.errors.map((item) => <li key={item.line}>第 {item.line} 行：{item.messages.join("；")}</li>)}</ul>}
          <button className="primary-button full" onClick={() => void runCommit()} disabled={preview.errors.length > 0 || preview.total === 0}>確認匯入 {preview.total} 列</button>
        </div>}
      </section>
    </div>}
  </main>;
}
