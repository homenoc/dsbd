import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react'
import {resolve} from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: './src',
  build: {
    rollupOptions: {
      input: {
        add_service: resolve(__dirname, './src/add_service/index.html'),
        add_connection: resolve(__dirname, './src/add_connection/index.html'),
      }
    }
  }
})
