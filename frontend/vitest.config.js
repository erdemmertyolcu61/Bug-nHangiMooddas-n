import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// Ayrı config: prod vite.config.js'teki PWA/sitemap eklentilerini testlerde
// çalıştırmadan, yalnızca React + jsdom ortamıyla birim testleri koşar.
export default defineConfig({
  plugins: [react()],
  // Bileşen testlerinde JSX klasik runtime'a (React.createElement) derleniyordu →
  // dosyalarda `import React` olmadan "React is not defined" hatası. Uygulama
  // kodu React 19 otomatik runtime kullanır; test ortamı da aynı olmalı.
  esbuild: { jsx: 'automatic' },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
    include: ['src/**/*.{test,spec}.{js,jsx}'],
  },
});
