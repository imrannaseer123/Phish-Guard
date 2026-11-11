import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: '/static/dist/',
  build: {
    outDir: path.resolve(import.meta.dirname, '../static/dist'),
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(import.meta.dirname, 'src/main.jsx'),
      output: {
        entryFileNames: 'assets/app.js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'assets/app.css';
          }
          return 'assets/[name]-[hash][extname]';
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://127.0.0.1:5000',
      '/oauth': 'http://127.0.0.1:5000',
      '/logout': 'http://127.0.0.1:5000',
      '/email': 'http://127.0.0.1:5000',
      '/history/clear': 'http://127.0.0.1:5000',
      '/feedback': 'http://127.0.0.1:5000',
      '/export': 'http://127.0.0.1:5000',
      '/chatbot': 'http://127.0.0.1:5000',
      '/ascend/whatif/simulate': 'http://127.0.0.1:5000',
      '/ascend/feedback': 'http://127.0.0.1:5000',
    },
  },
});
