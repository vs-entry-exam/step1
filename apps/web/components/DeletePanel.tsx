"use client";

import React, { useState } from 'react';
import { deleteDocs, DeleteResponse } from '../lib/api';
import { LoadingButton } from './LoadingButton';
import { Notice } from './Notice';

export function DeletePanel() {
  const [title, setTitle] = useState('');
  const [page, setPage] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [deleted, setDeleted] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDelete = async () => {
    if (!title.trim()) { setError('Please enter title'); return; }
    if (!confirm('Are you sure you want to delete? This action cannot be undone.')) return;
    setLoading(true); setError(null); setDeleted(null);
    try {
      const pageNum = page.trim() ? parseInt(page.trim(), 10) : undefined;
      const data: DeleteResponse = await deleteDocs({ title: title.trim(), page: pageNum });
      setDeleted(data.deleted ?? 0);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? e?.message ?? 'Delete failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel col">
      <h3 style={{ margin: 0 }}>Delete (by title / optional page)</h3>
      <div className="row" style={{ alignItems: 'flex-end' }}>
        <div className="col" style={{ flex: 2 }}>
          <label htmlFor="delTitle">title (filename)</label>
          <input id="delTitle" type="text" placeholder="sample.pdf"
            value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="col" style={{ maxWidth: 160 }}>
          <label htmlFor="delPage">page (optional)</label>
          <input id="delPage" type="number" min={1}
            value={page}
            onChange={(e) => setPage(e.target.value)} />
        </div>
        <div className="row" style={{ gap: 8 }}>
          <LoadingButton variant="secondary" onClick={() => { setTitle(''); setPage(''); setDeleted(null); setError(null); }}>Reset</LoadingButton>
          <LoadingButton onClick={onDelete} loading={loading} disabled={!title.trim()}>Delete</LoadingButton>
        </div>
      </div>
      {loading && <Notice>Deleting...</Notice>}
      {deleted != null && <Notice kind="success">deleted: {deleted}</Notice>}
      {error && <Notice kind="error">Error: {error}</Notice>}
    </section>
  );
}

