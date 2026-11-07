import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// The site reads the committed corpus and results files from the repo at build time,
// so every number on the page is generated or computed, never typed.
export default defineConfig({
  base: '/local-first-ai/',
  plugins: [react()],
  server: { fs: { allow: ['..'] } },
});
