'use client';

import React, { useState } from 'react';
import { LoadingButton } from '../../components/LoadingButton';
import { Notice } from '../../components/Notice';
import { AskRequest, askAgent, toErrorMessage } from '../../lib/api';

export default function AgentPage() {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<string>('');

  const submit = async () => {
    setLoading(true);
    setError(null);
    setAnswer('');
    try {
      const payload: AskRequest = { question, top_k: topK };
      const data = await askAgent(payload);
      setAnswer(data.answer);
    } catch (e: any) {
      setError(toErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="panel col">
      <div className="col">
        <label htmlFor="q">Question (Agent)</label>
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
        <LoadingButton onClick={submit} loading={loading} disabled={!question.trim()}>Ask (Agent)</LoadingButton>
      </div>

      {loading && <Notice>질의 중...</Notice>}
      {error && <Notice kind="error">에러: {error}</Notice>}
      {answer && (
        <div className="col" style={{ marginTop: 12 }}>
          <h3 style={{ margin: 0 }}>Answer</h3>
          <div className="panel" style={{ background: '#0e1529' }}>{answer}</div>
        </div>
      )}
    </main>
  );
}
