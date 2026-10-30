import { screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';

describe('application entry point', () => {
  afterEach(() => {
    document.body.innerHTML = '';
    vi.resetModules();
  });

  it('mounts the app into #root', async () => {
    document.body.innerHTML = '<div id="root"></div>';

    await import('@/main');

    expect(await screen.findByRole('heading', { level: 1 })).toBeVisible();
  });

  it('fails with a clear error when #root is missing', async () => {
    await expect(import('@/main')).rejects.toThrow('Root element #root not found');
  });
});
