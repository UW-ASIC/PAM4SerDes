import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // GitHub Pages serves the site at https://uw-asic.github.io/PAM4SerDes/, so every
  // asset URL needs the repository name in front. Must match the repository name exactly.
  base: '/PAM4SerDes/',
  server: {
    fs: {
      // The project's Markdown pages and diagrams live outside docs/, in
      // analog/PAM4SerDes/docs/ and CHANGELOGS.md (see src/utils/contentLoader.ts).
      // The dev server only serves files outside docs/ if the repository root is allowed.
      allow: ['..'],
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  }
})
