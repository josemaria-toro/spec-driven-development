import { fileURLToPath } from 'node:url';

import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  test: {
    coverage: {
      // main.tsx only mounts the app; it is covered by the integration test.
      exclude: ['src/main.tsx', 'src/**/*.test.{ts,tsx}', 'src/vite-env.d.ts'],
      include: ['src/**/*.{ts,tsx}'],
      provider: 'v8',
      reporter: ['text'],
      thresholds: { branches: 80, functions: 80, lines: 80, statements: 80 },
    },
    environment: 'jsdom',
    include: ['src/**/*.test.{ts,tsx}'],
    setupFiles: ['./tests/setup.ts'],
  },
});
