import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/hm-recommendation-analysis/',
  assetsInclude: ['**/*.glb'],
  build: {
    outDir: '../docs',
  },
})
