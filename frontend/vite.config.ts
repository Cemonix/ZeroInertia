import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import { loadEnv } from 'vite'
import { execSync } from 'child_process'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      vue(),
      // Generate service worker with environment variables
      {
        name: 'generate-service-worker',
        buildStart() {
          console.log('🔧 Generating service worker with environment variables...')
          try {
            execSync('node scripts/generate-sw.js', {
              stdio: 'inherit',
              env: { ...process.env, ...env }
            })
          } catch (error) {
            console.error('❌ Failed to generate service worker:', error)
            throw error
          }
        }
      }
    ],
    resolve: {
        alias: {
        '@': path.resolve(__dirname, './src'),
        'vue': 'vue/dist/vue.esm-bundler.js'
      }
    },
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false
        }
      }
    },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./src/tests/setup.ts'],
      alias: {
        '@': path.resolve(__dirname, './src')
      },
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html'],
        exclude: [
          'node_modules/',
          'src/tests/',
          '**/*.spec.ts',
          '**/*.test.ts',
          '**/types.ts',
          '**/models/',
        ],
      },
    },
  }
})
