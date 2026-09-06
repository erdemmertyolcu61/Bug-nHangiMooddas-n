import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist', 'ios', 'android', 'node_modules']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    rules: {
      // Boş `catch {}` bu kod tabanında bilinçli bir desendir: veri yerel-öncelikli
      // tutulur (localStorage tek doğru kaynak), sunucu senkronu "best effort"tur ve
      // başarısızlığı akışı bozmamalıdır. Kural bu sözleşmeyi yansıtsın — boş `if`/
      // `for` blokları hâlâ hata verir.
      'no-empty': ['error', { allowEmptyCatch: true }],
    },
  },
  {
    // Test dosyaları Vitest global'lerini kullanır (describe/it/expect/vi).
    files: ['**/*.{test,spec}.{js,jsx}'],
    languageOptions: {
      globals: { ...globals.browser, ...globals.node, vi: 'readonly' },
    },
  },
])
