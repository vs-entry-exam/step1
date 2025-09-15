'use client';

import { useState } from 'react';
import { api, AskRequest, AskResponse } from '../lib/api';

export default function AskPage() {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<string>('');
  const [sources, setSources] = useState<AskResponse['sources']>([]);

  const submit = async () => {
    setLoading(true);
    setError(null);
    setAnswer('');
    setSources([]);
    try {
      const payload: AskRequest = { question, top_k: topK };
      const { data } = await api.post<AskResponse>('/ask', payload, {
        headers: { 'Content-Type': 'application/json' },
      });
      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (e: any) {
      setError(e?.response?.data?.detail ?? e?.message ?? 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="panel col">
      <div className="col">
        <label htmlFor="q">Question</label>
        <textarea id="q" rows={4} placeholder="질문을 입력하세요"
          value={question} onChange={(e) => setQuestion(e.target.value)} />
      </div>
      <div className="row">
        <div className="col" style={{ maxWidth: 160 }}>
          <label htmlFor="topk">top_k</label>
          <input id="topk" type="number" min={1} max={20} value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value || '1', 10))} />
        </div>
        <div style={{ flex: 1 }} />
        <button onClick={submit} disabled={loading || !question.trim()}>Ask</button>
      </div>

      {loading && <p className="muted">질의 중...</p>}
      {error && <p className="accent">에러: {error}</p>}
      {answer && (
        <div className="col" style={{ marginTop: 12 }}>
          <h3 style={{ margin: 0 }}>Answer</h3>
          <div className="panel" style={{ background: '#0e1529' }}>{answer}</div>
        </div>
      )}
      {sources?.length > 0 && (
        <div className="col" style={{ marginTop: 12 }}>
          <h3 style={{ margin: 0 }}>Sources</h3>
          <ul className="sources">
            {sources.map((s, i) => (
              <li key={i}>
                <span className="muted">[{s.title}{s.page != null ? `:${s.page}` : ''}]</span>
                {s.score != null && <span className="muted"> · score: {s.score.toFixed(3)}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </main>
  );
}

