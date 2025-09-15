import React from 'react';
import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LoadingButton } from '../components/LoadingButton';
import { Notice } from '../components/Notice';

describe('components', () => {
  it('LoadingButton shows loading state', () => {
    render(<LoadingButton loading>Run</LoadingButton>);
    expect(screen.getByRole('button')).toHaveTextContent('...');
  });

  it('Notice kinds render with text', () => {
    const { rerender } = render(<Notice>info</Notice>);
    expect(screen.getByText('info')).toBeInTheDocument();
    rerender(<Notice kind="error">error</Notice>);
    expect(screen.getByText('error')).toBeInTheDocument();
    rerender(<Notice kind="success">ok</Notice>);
    expect(screen.getByText('ok')).toBeInTheDocument();
  });
});
