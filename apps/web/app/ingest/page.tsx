'use client';

import React, { useState } from 'react';
import { ingestFiles, deleteDocs, DeleteResponse, toErrorMessage } from '../../lib/api';
import { LoadingButton } from '../../components/LoadingButton';
import { Notice } from '../../components/Notice';

interface IngestResponse { indexed: number }

export default function IngestPage() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [indexed, setIndexed] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Delete controls
  const [delTitle, setDelTitle] = useState('');
  const [delPage, setDelPage] = useState<string>('');
  const [delLoading, setDelLoading] = useState(false);
  const [delResult, setDelResult] = useState<number | null>(null);
  const [delError, setDelError] = useState<string | null>(null);

  const onSubmit = async () => {
    if (!files || files.length === 0) return;
    setLoading(true);
    setError(null);
    setIndexed(null);
    try {
      const data: IngestResponse = await ingestFiles(files);
      setIndexed(data.indexed);
    } catch (e: any) {
      setError(toErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="col" style={{ gap: 16 }}>
      <section className="panel col">
        <h3 style={{ margin: 0 }}>Upload</h3>
        <div className="col">
          <label htmlFor="files">Select files (PDF/MD/TXT)</label>
          <input id="files" type="file" multiple onChange={(e) => setFiles(e.target.files)} />
        </div>
        <div className="row">
          <LoadingButton onClick={onSubmit} loading={loading} disabled={!files || files.length === 0}>Upload</LoadingButton>
          {loading && <Notice>Uploading / indexing...</Notice>}
        </div>
        {indexed != null && (<Notice kind="success">indexed: {indexed}</Notice>)}
        {error && (<Notice kind="error">Error: {error}</Notice>)}
      </section>

      <section className="panel col">
        <h3 style={{ margin: 0 }}>Delete (by title / optional page)</h3>
        <div className="row" style={{ alignItems: 'flex-end' }}>
          <div className="col" style={{ flex: 2 }}>
            <label htmlFor="delTitle">title (filename)</label>
            <input id="delTitle" type="text" placeholder="sample.pdf"
              value={delTitle} onChange={(e) => setDelTitle(e.target.value)} />
          </div>
          <div className="col" style={{ maxWidth: 160 }}>
            <label htmlFor="delPage">page (optional)</label>
            <input id="delPage" type="number" min={1}
              value={delPage}
              onChange={(e) => setDelPage(e.target.value)} />
          </div>
          <div className="row" style={{ gap: 8 }}>
            <LoadingButton variant="secondary" onClick={async () => {
              setDelTitle(''); setDelPage(''); setDelResult(null); setDelError(null);
            }}>Reset</LoadingButton>
            <LoadingButton onClick={async () => {
              if (!delTitle.trim()) { setDelError('Please enter title'); return; }
              if (!confirm('Are you sure you want to delete? This action cannot be undone.')) return;
              setDelLoading(true); setDelError(null); setDelResult(null);
              try {
                const pageNum = delPage.trim() ? parseInt(delPage.trim(), 10) : undefined;
                const data: DeleteResponse = await deleteDocs({ title: delTitle.trim(), page: pageNum });
                setDelResult(data.deleted ?? 0);
              } catch (e: any) {
                setDelError(toErrorMessage(e));
              } finally {
                setDelLoading(false);
              }
            }} loading={delLoading} disabled={!delTitle.trim()}>Delete</LoadingButton>
          </div>
        </div>
        {delLoading && <Notice>Deleting...</Notice>}
        {delResult != null && <Notice kind="success">deleted: {delResult}</Notice>}
        {delError && <Notice kind="error">Error: {delError}</Notice>}
      </section>
    </main>
  );
}
