import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  // Código generado o de terceros: reportes de cobertura y de herramientas, entorno de Python
  globalIgnores(['dist', 'backend/venv', 'docs/cobertura_html', 'docs/evidencias', '.demo']),
  {
    // Configuración de Cypress (Node) y pruebas E2E (Mocha + Cypress)
    files: ['cypress.config.js', 'cypress/**/*.js'],
    languageOptions: {
      globals: { ...globals.node, ...globals.mocha, cy: 'readonly', Cypress: 'readonly', expect: 'readonly' },
    },
  },
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    rules: {
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
    },
  },
])
