export type Stage = "靈感" | "腳本" | "製作中" | "待發布" | "已發布";

export type ContentKind = "Podcast" | "長片" | "Shorts" | "SEO 文章" | "IG 輪播" | "FB 貼文" | "復盤" | "其他";

export type AssetType = "簡報" | "圖片" | "影片" | "音檔" | "腳本" | "逐字稿" | "參考資料" | "其他";

export type ContentAsset = {
  id: string;
  label: string;
  type: AssetType;
  url: string;
  note?: string;
};

export type ContentItem = {
  id: string;
  title: string;
  kind: ContentKind;
  stage: Stage;
  due: string;
  next: string;
  accent: "purple" | "pink" | "lime" | "blue";
  /** Podcast 等母項為 null；衍生內容必須連回母項。 */
  parentId: string | null;
  releaseAt?: string;
  sourceUrl?: string;
  scriptSections?: string[];
  assets?: ContentAsset[];
};

export type Task = {
  id: string;
  label: string;
  detail: string;
  done: boolean;
  contentId: string;
  dueAt?: string;
  requiresApproval: boolean;
  approved?: boolean;
};

export const stages: Stage[] = ["靈感", "腳本", "製作中", "待發布", "已發布"];

const taipei = new Intl.DateTimeFormat("zh-TW", {
  timeZone: "Asia/Taipei",
  month: "numeric",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

function addDays(releaseAt: Date, days: number, hour: number, minute: number) {
  const result = new Date(releaseAt);
  result.setUTCDate(result.getUTCDate() + days);
  result.setUTCHours(hour - 8, minute, 0, 0);
  return result;
}

/**
 * 每週一正片的固定內容節奏。這只建立任務，絕不替使用者直接發布。
 */
export function createPodcastReleaseTasks(contentId: string, releaseAt: string): Task[] {
  const release = new Date(releaseAt);
  const schedule = [
    [0, 12, 15, "發布本集主題文", "FB／IG 主題文。發送前須確認文案與視覺。", true],
    [0, 20, 30, "發布限動或預告", "確認預告沒有為湊秒數切斷語意。", true],
    [2, 20, 30, "發布第 1 支節目精華", "同步準備 IG Reels、FB Reels、YouTube Shorts。", true],
    [4, 12, 0, "發布第 2 支節目精華", "同步準備 IG Reels、FB Reels、YouTube Shorts。", true],
    [7, 9, 0, "建立第 7 天復盤", "回填播放、完播、互動與有效的內容判斷。", false],
    [30, 9, 0, "建立第 30 天復盤", "確認短期訊號是否真的轉成長期有效規則。", false],
  ] as const;

  return schedule.map(([days, hour, minute, label, detail, requiresApproval], index) => {
    const dueAt = addDays(release, days, hour, minute);
    return {
      id: `${contentId}-routine-${index}`,
      label,
      detail,
      done: false,
      contentId,
      dueAt: dueAt.toISOString(),
      requiresApproval,
      approved: false,
    };
  });
}

export function formatTaipei(iso?: string) {
  return iso ? taipei.format(new Date(iso)) : "未排期";
}
