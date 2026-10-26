import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 关键：把 /api 开头的请求转发到后端 8000 端口
// 有了代理，浏览器就认为前后端同源，跨域问题根本不会出现
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
