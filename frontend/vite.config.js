import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    watch: {
      // Polling necesario para HMR en bind mounts de Docker / WSL2.
      usePolling: true,
    },
  },
});
