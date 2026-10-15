import { getCollection, type CollectionEntry } from 'astro:content';

// publishAt（ISO，含 +08:00）未到的文章不出現在任何頁面或 sitemap；週四 10:00 排程部署時才上線。
export function isPublished(post: CollectionEntry<'blog'>, now = new Date()) {
  if (!post.data.publishAt) return true;
  return new Date(post.data.publishAt).getTime() <= now.getTime();
}

export async function getPublishedPosts() {
  return (await getCollection('blog')).filter((post) => isPublished(post));
}
