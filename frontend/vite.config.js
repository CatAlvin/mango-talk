import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
    allowedHosts: ['mango-talk.chenglan.tech'],
    hmr: {
      host: 'mango-talk.chenglan.tech',
      protocol: 'ws',
      clientPort: 80,
    },
  },
})