import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  publicDir: 'public',
  server: {
    port: 3006,
    proxy: {
      '/api': {
        target: 'http://localhost:5008',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:5008',
        changeOrigin: true,
        ws: true
      }
    }
  },
  build: {
    outDir: 'build',
    sourcemap: false,
    emptyOutDir: true
  }
})
