'use client';

import { useState } from 'react';
import { api } from '../../lib/api';

interface IngestResponse { indexed: number }

export default function IngestPage() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [indexed, setIndexed] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async () => {
    if (!files || files.length === 0) return;
    setLoading(true);
    setError(null);
    setIndexed(null);
    const form = new FormData();
    Array.from(files).forEach((f) => form.append('files', f));
    try {
      const { data } = await api.post<IngestResponse>('/ingest', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setIndexed(data.indexed);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? e?.message ?? 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="panel col">
      <div className="col">
        <label htmlFor="files">파일 선택 (PDF/MD/TXT)</label>
        <input id="files" type="file" multiple onChange={(e) => setFiles(e.target.files)} />
      </div>
      <div className="row">
        <button onClick={onSubmit} disabled={loading || !files || files.length === 0}>Ingest</button>
        {loading && <span className="muted"> 업로드/인덱싱 중...</span>}
      </div>
      {indexed != null && (
        <p className="accent2">indexed: {indexed}</p>
      )}
      {error && (
        <p className="accent">에러: {error}</p>
      )}
    </main>
  );
}

