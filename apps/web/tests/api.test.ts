import { afterEach, describe, expect, it, vi } from 'vitest';

// Mock axios before importing the module under test
vi.mock('axios', () => {
  const post = vi.fn();
  const del = vi.fn();
  const create = vi.fn(() => ({ post, delete: del }));
  return { __esModule: true, default: { create }, _post: post, _del: del } as any;
});

describe('lib/api', () => {
  it('askQuestion posts to /ask', async () => {
    const axiosMock: any = await import('axios');
    axiosMock._post.mockResolvedValueOnce({ data: { answer: 'ok', sources: [] } });
    const mod = await import('../lib/api');
    const res = await mod.askQuestion({ question: 'q', top_k: 3 });
    expect(res.answer).toBe('ok');
    expect(axiosMock._post).toHaveBeenCalledWith('/ask', { question: 'q', top_k: 3 }, expect.any(Object));
  });

  it('ingestFiles posts multipart to /rag', async () => {
    const axiosMock: any = await import('axios');
    axiosMock._post.mockResolvedValueOnce({ data: { indexed: 2 } });
    const { ingestFiles } = await import('../lib/api');
    const file = new File([new Blob(['abc'])], 'a.txt', { type: 'text/plain' });
    const res = await ingestFiles([file]);
    expect(res.indexed).toBe(2);
    expect(axiosMock._post).toHaveBeenCalledWith('/rag', expect.any(FormData), expect.any(Object));
  });

  it('deleteDocs sends body in DELETE', async () => {
    const axiosMock: any = await import('axios');
    axiosMock._del.mockResolvedValueOnce({ data: { deleted: 1 } });
    const { deleteDocs } = await import('../lib/api');
    const res = await deleteDocs({ title: 'a.txt' });
    expect(res.deleted).toBe(1);
    expect(axiosMock._del).toHaveBeenCalledWith('/docs', expect.objectContaining({ data: { title: 'a.txt' } }));
  });

  afterEach(async () => {
    const axiosMock: any = await import('axios');
    axiosMock._post.mockReset();
    axiosMock._del.mockReset();
  });
});
