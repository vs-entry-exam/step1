'use client';

import React from 'react';
import { UploadPanel } from '../../components/UploadPanel';
import { DeletePanel } from '../../components/DeletePanel';

export default function RagPage() {
  return (
    <main className="col" style={{ gap: 16 }}>
      <UploadPanel />
      <DeletePanel />
    </main>
  );
}
