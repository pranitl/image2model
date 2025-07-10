import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig(({ mode }) => {
  // Load env file from the root directory (parent of frontend-svelte)
  const env = loadEnv(mode, '../', '');
  
  return {
    plugins: [
      sveltekit(),
      process.env.ANALYZE && visualizer({
        filename: './stats.html',
        open: true,
        gzipSize: true,
        brotliSize: true,
      })
    ].filter(Boolean),
    
    build: {
      // Production optimizations
      minify: mode === 'production' ? 'terser' : false,
      terserOptions: {
        compress: {
          drop_console: mode === 'production',
          drop_debugger: mode === 'production'
        }
      },
      reportCompressedSize: true,
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['svelte', '@sveltejs/kit'],
            'animations': ['$lib/actions/animations.js']
          }
        }
      }
    },
    
    server: {
      host: '0.0.0.0',
      port: parseInt(env.FRONTEND_PORT) || 3000,
      proxy: {
        '/api': {
          target: process.env.NODE_ENV === 'production' ? 'http://backend:8000' : 'http://localhost:8000',
          changeOrigin: true
        },
        '/ws': {
          target: process.env.NODE_ENV === 'production' ? 'ws://backend:8000' : 'ws://localhost:8000',
          ws: true,
          changeOrigin: true
        }
      }
    },
    
    // Define environment variables that should be exposed to the client
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
      // Explicitly pass PUBLIC_API_URL to the client-side code
      'import.meta.env.PUBLIC_API_URL': JSON.stringify(process.env.PUBLIC_API_URL)
    }
  };
});
