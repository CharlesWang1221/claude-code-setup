import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://beyond-ans.com',
  output: 'static',
  integrations: [sitemap()],
});
