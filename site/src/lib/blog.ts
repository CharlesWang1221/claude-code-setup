import { getCollection, type CollectionEntry } from 'astro:content';

// publishAt（ISO，含 +08:00）未到的文章不出現在任何頁面或 sitemap；週四 10:00 排程部署時才上線。
export function isPublished(post: CollectionEntry<'blog'>, now = new Date()) {
  if (!post.data.publishAt) return true;
  return new Date(post.data.publishAt).getTime() <= now.getTime();
}

export async function getPublishedPosts() {
  // mirrorOf：FB 同步回來的居易長文，網站上已有原文，不重複列出
  return (await getCollection('blog')).filter((post) => isPublished(post) && !post.data.mirrorOf);
}
