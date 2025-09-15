import React from 'react';
import { describe, expect, it, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

describe('Ask page', async () => {
  it('submits question and shows answer', async () => {
    const api = await import('../lib/api');
    vi.spyOn(api, 'askQuestion').mockResolvedValue({ answer: '테스트 답변', sources: [] });
    const Page = (await import('../app/agent/page')).default;

    render(<Page />);
    const textarea = screen.getByLabelText(/Question/i);
    fireEvent.change(textarea, { target: { value: '무엇?' } });
    fireEvent.click(screen.getByRole('button', { name: /ask/i }));

    expect(await screen.findByText('Answer')).toBeInTheDocument();
    expect(await screen.findByText('테스트 답변')).toBeInTheDocument();
  });
});
