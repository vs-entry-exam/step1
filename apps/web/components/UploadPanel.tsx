"use client";

import React, { useState } from 'react';
import { ingestFiles } from '../lib/api';
import { LoadingButton } from './LoadingButton';
import { Notice } from './Notice';

export function UploadPanel({ onDone }: { onDone?: (indexed: number) => void }) {
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [indexed, setIndexed] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onUpload = async () => {
    if (!files || files.length === 0) return;
    setLoading(true);
    setError(null);
    setIndexed(null);
    try {
      const data = await ingestFiles(files);
      setIndexed(data.indexed);
      onDone?.(data.indexed);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? e?.message ?? 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="panel col">
      <h3 style={{ margin: 0 }}>Upload</h3>
      <div className="col">
        <label htmlFor="files">Select files (PDF/MD/TXT)</label>
        <input id="files" type="file" multiple onChange={(e) => setFiles(e.target.files)} />
      </div>
      <div className="row">
        <LoadingButton onClick={onUpload} loading={loading} disabled={!files || files.length === 0}>Upload</LoadingButton>
        {loading && <Notice>Uploading / indexing...</Notice>}
      </div>
      {indexed != null && (<Notice kind="success">indexed: {indexed}</Notice>)}
      {error && (<Notice kind="error">Error: {error}</Notice>)}
    </section>
  );
}

