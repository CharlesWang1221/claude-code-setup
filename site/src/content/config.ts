import { defineCollection, z } from 'astro:content';

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.string(),
    description: z.string().optional(),
    image: z.string().optional(),
    fbPostId: z.string().optional(),
    tags: z.array(z.string()).optional(),
    publishAt: z.string().optional(),
    mirrorOf: z.string().optional(),
    faq: z.array(z.object({ q: z.string(), a: z.string() })).optional(),
  }),
});

// 單集重點：檔名用集數（s3ep11.md），單集頁依季／集自動對上
const highlights = defineCollection({
  type: 'content',
  schema: z.object({
    summary: z.string(),
    chapters: z.array(z.object({ time: z.string(), title: z.string() })).optional(),
    quotes: z.array(z.object({ text: z.string(), speaker: z.string() })).optional(),
    faq: z.array(z.object({ q: z.string(), a: z.string() })).optional(),
    related: z.array(z.string()).optional(),
  }),
});

export const collections = { blog, highlights };
