import { defineConfig, devices } from '@playwright/test';

const PORT = '4173';

// Every critical flow runs at mobile, tablet and desktop widths (WCAG 2.2 AA, responsive rule).
export default defineConfig({
  forbidOnly: Boolean(process.env.CI),
  fullyParallel: true,
  projects: [
    {
      name: 'mobile',
      use: { ...devices['Desktop Chrome'], viewport: { height: 640, width: 360 } },
    },
    {
      name: 'tablet',
      use: { ...devices['Desktop Chrome'], viewport: { height: 1024, width: 768 } },
    },
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'], viewport: { height: 800, width: 1280 } },
    },
  ],
  reporter: process.env.CI ? [['html', { open: 'never' }], ['list']] : 'list',
  retries: 0,
  testDir: './tests/e2e',
  use: {
    baseURL: `http://localhost:${PORT}`,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  // Runs against the built app, as in CI.
  webServer: {
    command: `pnpm build && pnpm exec vite preview --port ${PORT} --strictPort`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    url: `http://localhost:${PORT}`,
  },
});
