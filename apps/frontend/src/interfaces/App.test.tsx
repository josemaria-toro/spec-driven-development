import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { App } from '@/interfaces/App';

describe('App', () => {
  it('shows the page heading', () => {
    render(<App />);

    expect(
      screen.getByRole('heading', { level: 1, name: 'Create a development project' }),
    ).toBeVisible();
  });

  it('has a banner and a main landmark', () => {
    render(<App />);

    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('offers a skip link that targets the main content', () => {
    render(<App />);

    const link = screen.getByRole('link', { name: 'Skip to main content' });

    expect(link).toHaveAttribute('href', '#main-content');
    expect(screen.getByRole('main')).toHaveAttribute('id', 'main-content');
  });
});
