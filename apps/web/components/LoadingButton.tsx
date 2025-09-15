"use client";

import React from "react";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  loading?: boolean;
  variant?: 'primary' | 'secondary';
};

export function LoadingButton({ loading, disabled, children, variant = 'primary', ...rest }: Props) {
  const cls = variant === 'secondary' ? 'secondary' : '';
  return (
    <button className={cls} disabled={disabled || loading} {...rest}>
      {loading ? '... ' : ''}{children}
    </button>
  );
}

