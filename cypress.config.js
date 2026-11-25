import { defineConfig } from 'cypress';

// Pruebas de integración (Segunda parte, sección 4 / Apéndice B).
// Variables: CYPRESS_API, CYPRESS_SC_EMAIL, CYPRESS_SC_PASS y, para el flujo E2E,
// CYPRESS_BASE_URL (por defecto el frontend desplegado en Vercel).
export default defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL || 'https://shifts-chash-version-amaya.vercel.app',
    supportFile: false,
    video: false,
    defaultCommandTimeout: 15000,
    responseTimeout: 120000, // la API en Render puede tardar en despertar (D-09)
  },
});
