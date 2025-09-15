import { describe, expect, it } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

describe('Upload page', async () => {
  it('shows error when deleting without title', async () => {
    const Page = (await import('../app/ingest/page')).default;
    render(<Page />);
    fireEvent.click(screen.getByRole('button', { name: /delete/i }));
    expect(await screen.findByText(/title을 입력하세요/)).toBeInTheDocument();
  });
});

