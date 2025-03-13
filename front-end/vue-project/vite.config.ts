import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    plugins: [
      vue(),
      vueJsx(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
    proxy: {
      '/summary': {
          target: env.VITE_READER_PATH,
          changeOrigin: true,
          secure: false
        },
        '/pico': {
          target: env.VITE_READER_PATH,
          changeOrigin: true,
          secure: false
        }
      ,
      // Account Registration (port 5001)
      '/api/register': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api\/register/, '')
      },

      // Account Login (port 5002)
      '/api/login': {
        target: 'http://localhost:5002',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api\/login/, '')
      },
      // Some calls might be /login/refresh_cookie, /login/logout, etc.
      // Just keep the prefix /login in your code.

      // Account Messages (port 5007)
      '/api/messages': {
        target: 'http://localhost:5007',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api\/messages/, '')
      },

      // Data Reader (port 5003)
      '/api/reader': {
        target: 'http://localhost:5003',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api\/reader/, '')
      },

      // Warning Editor (port 5004) - if you have calls to it
      '/api/warning': {
        target: 'http://localhost:5004',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api\/warning/, '')
      },

      // Assets Editor (port 5011)
      '/api/editor': {
        target: 'http://localhost:5011',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api\/editor/, '')
      },

      // Assets Reader (port 5010)
      '/api/assets-reader': {
        target: 'http://localhost:5010',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api\/assets-reader/, '')
      },
    }
  },
  };
});
