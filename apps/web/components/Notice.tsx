"use client";
import React from 'react';

export function Notice({ kind = 'info', children }: { kind?: 'info' | 'error' | 'success'; children: React.ReactNode }) {
  const cls = kind === 'error' ? 'accent' : kind === 'success' ? 'accent2' : 'muted';
  const role = kind === 'error' ? 'alert' : kind === 'success' ? 'status' : undefined;
  return <p className={cls} role={role}>{children}</p>;
}
