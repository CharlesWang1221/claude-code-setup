import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://podcast-site-9hr.pages.dev',
  output: 'static',
  integrations: [sitemap()],
});
