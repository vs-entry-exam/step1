"use client";

export function Notice({ kind = 'info', children }: { kind?: 'info' | 'error' | 'success'; children: React.ReactNode }) {
  const cls = kind === 'error' ? 'accent' : kind === 'success' ? 'accent2' : 'muted';
  return <p className={cls}>{children}</p>;
}

