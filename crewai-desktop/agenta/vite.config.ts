import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
  clearScreen: false,
  
  // Configure server
  server: {
    port: 3000,
    strictPort: false, // Allow fallback to next available port
    host: true, // Listen on all addresses
    // Handle port in use
    hmr: { port: 3000 },
    watch: {
      // Watch backend directory for changes
      ignored: ['**/src-tauri/backend/**']
    },
    proxy: {
      // Proxy backend requests to Tauri backend server
      '/api': 'http://localhost:3001'
    }
  },

  // Configure build
  build: {
    target: process.env.TAURI_PLATFORM == "windows" ? "chrome105" : "safari13",
    minify: !process.env.TAURI_DEBUG ? "esbuild" : false,
    sourcemap: !!process.env.TAURI_DEBUG,
    outDir: "dist",
  },

  // Configure resolve aliases
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
      "@components": resolve(__dirname, "src/components"),
      "@assets": resolve(__dirname, "src/assets"),
    },
  },
});
