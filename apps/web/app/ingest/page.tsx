'use client';

import { useState } from 'react';
import { api, deleteDocs, DeleteResponse } from '../../lib/api';

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
    <main className="col" style={{ gap: 16 }}>
      <section className="panel col">
        <h3 style={{ margin: 0 }}>Upload</h3>
        <div className="col">
          <label htmlFor="files">파일 선택 (PDF/MD/TXT)</label>
          <input id="files" type="file" multiple onChange={(e) => setFiles(e.target.files)} />
        </div>
        <div className="row">
          <button onClick={onSubmit} disabled={loading || !files || files.length === 0}>Upload</button>
          {loading && <span className="muted"> 업로드/인덱싱 중...</span>}
        </div>
        {indexed != null && (
          <p className="accent2">indexed: {indexed}</p>
        )}
        {error && (
          <p className="accent">에러: {error}</p>
        )}
      </section>

      <section className="panel col">
        <h3 style={{ margin: 0 }}>Delete (by title / optional page)</h3>
        <div className="row" style={{ alignItems: 'flex-end' }}>
          <div className="col" style={{ flex: 2 }}>
            <label htmlFor="delTitle">title (파일명)</label>
            <input id="delTitle" type="text" placeholder="sample.pdf"
              value={delTitle} onChange={(e) => setDelTitle(e.target.value)} />
          </div>
          <div className="col" style={{ maxWidth: 160 }}>
            <label htmlFor="delPage">page (선택)</label>
            <input id="delPage" type="number" min={1}
              value={delPage}
              onChange={(e) => setDelPage(e.target.value)} />
          </div>
          <div className="row" style={{ gap: 8 }}>
            <button className="secondary" onClick={async () => {
              setDelTitle(''); setDelPage(''); setDelResult(null); setDelError(null);
            }}>Reset</button>
            <button onClick={async () => {
              if (!delTitle.trim()) { setDelError('title을 입력하세요'); return; }
              if (!confirm('정말 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) return;
              setDelLoading(true); setDelError(null); setDelResult(null);
              try {
                const pageNum = delPage.trim() ? parseInt(delPage.trim(), 10) : undefined;
                const data: DeleteResponse = await deleteDocs({ title: delTitle.trim(), page: pageNum });
                setDelResult(data.deleted ?? 0);
              } catch (e: any) {
                setDelError(e?.response?.data?.detail ?? e?.message ?? 'Delete failed');
              } finally {
                setDelLoading(false);
              }
            }} disabled={delLoading || !delTitle.trim()}>Delete</button>
          </div>
        </div>
        {delLoading && <p className="muted">삭제 중...</p>}
        {delResult != null && <p className="accent2">deleted: {delResult}</p>}
        {delError && <p className="accent">에러: {delError}</p>}
      </section>
    </main>
  );
}
