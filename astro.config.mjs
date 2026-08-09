import { defineConfig } from 'astro/config';

export default defineConfig({
  output: 'static',
  site: 'https://proof-it.pages.dev',
  base: '/',
  build: {
    format: 'file'
  }
});
