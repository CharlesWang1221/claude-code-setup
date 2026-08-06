"use client";

import { useEffect, useMemo, useState } from "react";

type Stage = "靈感" | "腳本" | "製作中" | "待發布" | "已發布";
type View = "今日推進" | "內容流轉" | "節奏日曆" | "復盤沉澱" | "規則庫";

type ContentItem = {
  id: number;
  title: string;
  type: string;
  stage: Stage;
  due: string;
  next: string;
  accent: "purple" | "pink" | "lime" | "blue";
};

type Task = { id: number; label: string; detail: string; done: boolean; related: string };

const stages: Stage[] = ["靈感", "腳本", "製作中", "待發布", "已發布"];

const initialContent: ContentItem[] = [
  { id: 1, title: "內容不是終點，它要推動一門生意", type: "Podcast／長片", stage: "腳本", due: "週四 14:00", next: "確認訪綱第 3 段", accent: "purple" },
  { id: 2, title: "你以為在努力，其實只是在逃避判斷", type: "Shorts", stage: "製作中", due: "週五", next: "挑 3 個 45 秒段落", accent: "pink" },
  { id: 3, title: "小公司不該把自動化當炫技", type: "SEO 文章", stage: "待發布", due: "週六 09:00", next: "補內部連結與封面", accent: "lime" },
  { id: 4, title: "AI 工作流不是省時間，是少做錯事", type: "IG 輪播", stage: "靈感", due: "下週", next: "寫出一個反直覺開頭", accent: "blue" },
  { id: 5, title: "S2EP12 上架後復盤", type: "復盤", stage: "已發布", due: "週日", next: "記錄前 72 小時數據", accent: "purple" },
];

const initialTasks: Task[] = [
  { id: 1, label: "確認下一集的衝突句", detail: "先決定觀眾會反駁哪一句", done: false, related: "內容不是終點" },
  { id: 2, label: "把 Shorts 素材切成 3 段", detail: "每段只保留一個觀點", done: false, related: "努力與逃避判斷" },
  { id: 3, label: "回填上一集的復盤", detail: "不要只寫播放數，要寫下次規則", done: false, related: "S2EP12" },
  { id: 4, label: "排好本週 Podcast 發佈", detail: "Firstory、YouTube、FB 預告", done: true, related: "內容節奏" },
];

function Icon({ name }: { name: "home" | "board" | "calendar" | "review" | "book" | "plus" | "arrow" | "check" }) {
  const paths = {
    home: <><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1V10Z" /></>,
    board: <><rect x="3" y="4" width="18" height="16" rx="2" /><path d="M8 4v16M15 4v16" /></>,
    calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M7 3v4M17 3v4M3 10h18" /></>,
    review: <><path d="M4 19.5V4.8A1.8 1.8 0 0 1 5.8 3h12.4A1.8 1.8 0 0 1 20 4.8v14.7L16 17l-4 2.5L8 17l-4 2.5Z" /><path d="M8 7h8M8 11h8" /></>,
    book: <><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v17H6.5A2.5 2.5 0 0 0 4 22V5.5ZM20 5.5A2.5 2.5 0 0 0 17.5 3H13v17h4.5A2.5 2.5 0 0 1 20 22V5.5Z" /></>,
    plus: <><path d="M12 5v14M5 12h14" /></>,
    arrow: <><path d="M5 12h14M13 6l6 6-6 6" /></>,
    check: <><path d="m5 12 4 4L19 6" /></>,
  };
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

function Badge({ children, accent }: { children: React.ReactNode; accent?: string }) {
  return <span className={`badge ${accent ?? ""}`}>{children}</span>;
}

export default function Home() {
  const [view, setView] = useState<View>("今日推進");
  const [content, setContent] = useState<ContentItem[]>(initialContent);
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [showComposer, setShowComposer] = useState(false);
  const [draft, setDraft] = useState("");
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const restore = window.setTimeout(() => {
      const saved = localStorage.getItem("creator-os-mvp");
      if (saved) {
        try {
          const parsed = JSON.parse(saved) as { content: ContentItem[]; tasks: Task[] };
          setContent(parsed.content);
          setTasks(parsed.tasks);
        } catch { /* 保留範例資料 */ }
      }
      setHydrated(true);
    }, 0);
    return () => window.clearTimeout(restore);
  }, []);

  useEffect(() => {
    if (hydrated) localStorage.setItem("creator-os-mvp", JSON.stringify({ content, tasks }));
  }, [content, tasks, hydrated]);

  const completion = useMemo(() => Math.round((tasks.filter((task) => task.done).length / tasks.length) * 100), [tasks]);
  const todayTasks = tasks.filter((task) => !task.done);

  function toggleTask(id: number) {
    setTasks((items) => items.map((task) => task.id === id ? { ...task, done: !task.done } : task));
  }

  function moveItem(id: number, stage: Stage) {
    setContent((items) => items.map((item) => item.id === id ? { ...item, stage } : item));
  }

  function addIdea() {
    const title = draft.trim();
    if (!title) return;
    setContent((items) => [{ id: Date.now(), title, type: "待定", stage: "靈感", due: "未排期", next: "先寫一句想反駁它的話", accent: "blue" }, ...items]);
    setTasks((items) => [{ id: Date.now() + 1, label: `判斷：${title}`, detail: "決定它服務哪個內容目標", done: false, related: "新靈感" }, ...items]);
    setDraft("");
    setShowComposer(false);
    setView("內容流轉");
  }

  const nav: { label: View; icon: Parameters<typeof Icon>[0]["name"] }[] = [
    { label: "今日推進", icon: "home" }, { label: "內容流轉", icon: "board" }, { label: "節奏日曆", icon: "calendar" }, { label: "復盤沉澱", icon: "review" }, { label: "規則庫", icon: "book" },
  ];

  return <main className="shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">不</span><span>CREATOR<br /><strong>OS</strong></span></div>
      <div className="workspace-label">不標準答案 · 內容營運</div>
      <nav aria-label="工作站主選單">
        {nav.map((item) => <button key={item.label} className={`nav-item ${view === item.label ? "active" : ""}`} onClick={() => setView(item.label)}><Icon name={item.icon} /><span>{item.label}</span></button>)}
      </nav>
      <div className="sidebar-foot">
        <div className="mini-progress"><div><span>本週節奏</span><strong>{completion}%</strong></div><div className="progress-track"><i style={{ width: `${completion}%` }} /></div><small>{tasks.filter((task) => task.done).length} / {tasks.length} 個關鍵任務完成</small></div>
        <p>資料目前只存在這台電腦的瀏覽器。</p>
      </div>
    </aside>

    <section className="workspace">
      <header className="topbar"><div><p className="eyebrow">2026 / 08 / 06 · THU</p><h1>{view}</h1></div><div className="header-actions"><button className="ghost-button" onClick={() => setView("復盤沉澱")}>本週復盤</button><button className="primary-button" onClick={() => setShowComposer(true)}><Icon name="plus" />收進一個靈感</button></div></header>
      {view === "今日推進" && <TodayView tasks={todayTasks} content={content} completion={completion} onToggle={toggleTask} onViewBoard={() => setView("內容流轉")} />}
      {view === "內容流轉" && <BoardView content={content} onMove={moveItem} />}
      {view === "節奏日曆" && <CalendarView content={content} />}
      {view === "復盤沉澱" && <ReviewView />}
      {view === "規則庫" && <RulesView />}
    </section>

    {showComposer && <div className="modal-backdrop" role="presentation" onMouseDown={() => setShowComposer(false)}><section className="composer" role="dialog" aria-modal="true" aria-labelledby="composer-title" onMouseDown={(event) => event.stopPropagation()}><button className="close" onClick={() => setShowComposer(false)} aria-label="關閉">×</button><p className="eyebrow">CAPTURE BEFORE IT VANISHES</p><h2 id="composer-title">先收下，晚點再判斷</h2><label htmlFor="idea">這個靈感想推動什麼？</label><textarea id="idea" autoFocus placeholder="例如：觀眾以為要更多自動化，其實先該砍掉不必要的流程。" value={draft} onChange={(event) => setDraft(event.target.value)} /><button className="primary-button full" onClick={addIdea}>放進內容流轉 <Icon name="arrow" /></button></section></div>}
  </main>;
}

function TodayView({ tasks, content, completion, onToggle, onViewBoard }: { tasks: Task[]; content: ContentItem[]; completion: number; onToggle: (id: number) => void; onViewBoard: () => void }) {
  const nextItem = content.find((item) => item.stage !== "已發布");
  return <div className="page-grid today-layout">
    <section className="hero-card"><p className="eyebrow">TODAY&apos;S ONE THING</p><h2>不是清完待辦，<br />是推動下一個結果。</h2><p className="hero-copy">今天只要讓一條內容往前走，其他事情才不會把你拖回忙碌的幻覺。</p><div className="hero-focus"><span>現在推進</span><strong>{nextItem?.title}</strong><button onClick={onViewBoard}>看內容位置 <Icon name="arrow" /></button></div></section>
    <section className="stat-card"><p>本週完成度</p><strong>{completion}%</strong><div className="ring" style={{ "--progress": `${completion * 3.6}deg` } as React.CSSProperties}><span>{tasks.length}<small>件待推進</small></span></div></section>
    <section className="panel tasks-panel"><div className="panel-heading"><div><p className="eyebrow">TODAY&apos;S PUSH</p><h2>今天推進</h2></div><Badge accent="pink">只留 {tasks.length} 件</Badge></div>{tasks.map((task) => <button className={`task-row ${task.done ? "done" : ""}`} key={task.id} onClick={() => onToggle(task.id)}><span className="check-box"><Icon name="check" /></span><span><strong>{task.label}</strong><small>{task.detail} · {task.related}</small></span></button>)}</section>
    <section className="panel rhythm-panel"><div className="panel-heading"><div><p className="eyebrow">THIS WEEK</p><h2>本週節奏</h2></div><button className="text-button">完整日曆</button></div>{content.slice(0, 4).map((item, index) => <div className="rhythm-row" key={item.id}><span className="date-pill">0{7 + index}<small>THU</small></span><i className={`dot ${item.accent}`} /><span><strong>{item.title}</strong><small>{item.type} · {item.stage}</small></span></div>)}</section>
  </div>;
}

function BoardView({ content, onMove }: { content: ContentItem[]; onMove: (id: number, stage: Stage) => void }) {
  return <div className="board-wrap">{stages.map((stage) => <section className="board-column" key={stage}><header><span>{stage}</span><Badge>{content.filter((item) => item.stage === stage).length}</Badge></header>{content.filter((item) => item.stage === stage).map((item) => <article className="content-card" key={item.id}><i className={`card-line ${item.accent}`} /><Badge accent={item.accent}>{item.type}</Badge><h3>{item.title}</h3><p>下一步：{item.next}</p><footer><span>{item.due}</span><select aria-label={`移動「${item.title}」的階段`} value={item.stage} onChange={(event) => onMove(item.id, event.target.value as Stage)}>{stages.map((option) => <option key={option}>{option}</option>)}</select></footer></article>)}</section>)}</div>;
}

function CalendarView({ content }: { content: ContentItem[] }) {
  const days = Array.from({ length: 31 }, (_, index) => index + 1);
  return <section className="panel calendar-panel"><div className="panel-heading"><div><p className="eyebrow">ONE SOURCE OF TRUTH</p><h2>2026 年 8 月</h2></div><Badge accent="lime">排程從內容主檔而來</Badge></div><div className="week-labels">{["日", "一", "二", "三", "四", "五", "六"].map((day) => <span key={day}>{day}</span>)}</div><div className="calendar-grid">{Array.from({ length: 6 }, (_, index) => <div key={`empty-${index}`} className="calendar-day muted" />)}{days.map((day) => { const item = content[day % content.length]; return <div key={day} className={`calendar-day ${day === 6 ? "today" : ""}`}><span>{day}</span>{[8, 14, 21, 28].includes(day) && <button className={`calendar-event ${item.accent}`}>{item.type}<small>{item.title.slice(0, 11)}…</small></button>}</div>})}</div></section>;
}

function ReviewView() { return <div className="review-layout"><section className="panel review-form"><p className="eyebrow">POST-PUBLISH REVIEW</p><h2>發布不是結束，<br />是下一次判斷的證據。</h2><div className="metric-row"><label>播放／觸及<input defaultValue="27,700" /></label><label>完播／互動<input defaultValue="1,870" /></label></div><label>這次真正有效的是什麼？<textarea defaultValue="開頭先承認自己也做錯過，留言比純工具教學多。" /></label><label>下次要遵守的規則<input defaultValue="每支工具片，先放一個錯誤現場。" /></label><button className="primary-button full">儲存這次復盤 <Icon name="check" /></button></section><section className="panel scorecard"><p className="eyebrow">LATEST SIGNAL</p><h2>別只看數字，<br />看它指向哪裡。</h2><div className="signal"><strong>4.8<span>/ 5</span></strong><p>觀眾理解度</p></div><div className="signal-list"><span>開頭鉤子 <b>有效</b></span><span>工具清單 <b className="weak">過長</b></span><span>CTA <b>需補強</b></span></div></section></div>; }

function RulesView() { const rules = ["每支工具片，先放一個錯誤現場。", "Podcast 上架後 72 小時內，一定填完復盤。", "Shorts 不是摘要：一支只留一個會被反駁的判斷。", "沒有明確服務目標的選題，不進日曆。"]; return <section className="panel rules-panel"><div className="panel-heading"><div><p className="eyebrow">WHAT WE LEARNED THE HARD WAY</p><h2>不是知識庫，是你的防呆系統。</h2></div><Badge accent="lime">4 條正在生效</Badge></div><div className="rules-list">{rules.map((rule, index) => <article key={rule}><span>0{index + 1}</span><p>{rule}</p><Badge>內容規則</Badge></article>)}</div></section>; }
