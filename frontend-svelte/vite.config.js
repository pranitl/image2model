import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '');
  
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
          target: `http://${env.BACKEND_HOST || 'backend'}:${env.BACKEND_PORT || 8000}`,
          changeOrigin: true
        },
        '/ws': {
          target: `ws://${env.BACKEND_HOST || 'backend'}:${env.BACKEND_PORT || 8000}`,
          ws: true,
          changeOrigin: true
        }
      }
    },
    
    // Define environment variables that should be exposed to the client
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString())
    }
  };
});
