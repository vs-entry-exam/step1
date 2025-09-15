import React from 'react';
import { describe, expect, it } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

describe('Upload page', async () => {
  it('shows error when deleting without title', async () => {
    const Page = (await import('../app/rag/page')).default;
    render(<Page />);
    fireEvent.click(screen.getByRole('button', { name: /delete/i }));
    // Error Notice renders with role="alert" when title is missing
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });
});
