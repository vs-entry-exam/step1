import { afterEach, describe, expect, it, vi } from 'vitest';
import axios from 'axios';
import { askQuestion, ingestFiles, deleteDocs } from '../lib/api';

vi.mock('axios');

const mockedAxios = axios as unknown as {
  create: (cfg: any) => any;
};

// Provide a faux axios instance with request methods we can spy on
const post = vi.fn();
const del = vi.fn();
mockedAxios.create = () => ({ post, delete: del });

afterEach(() => {
  post.mockReset();
  del.mockReset();
});

describe('lib/api', () => {
  it('askQuestion posts to /ask', async () => {
    post.mockResolvedValueOnce({ data: { answer: 'ok', sources: [] } });
    const res = await askQuestion({ question: 'q', top_k: 3 });
    expect(res.answer).toBe('ok');
    expect(post).toHaveBeenCalledWith('/ask', { question: 'q', top_k: 3 }, expect.any(Object));
  });

  it('ingestFiles posts multipart to /ingest', async () => {
    post.mockResolvedValueOnce({ data: { indexed: 2 } });
    const file = new File([new Blob(['abc'])], 'a.txt', { type: 'text/plain' });
    const res = await ingestFiles([file]);
    expect(res.indexed).toBe(2);
    expect(post).toHaveBeenCalledWith('/ingest', expect.any(FormData), expect.any(Object));
  });

  it('deleteDocs sends body in DELETE', async () => {
    del.mockResolvedValueOnce({ data: { deleted: 1 } });
    const res = await deleteDocs({ title: 'a.txt' });
    expect(res.deleted).toBe(1);
    expect(del).toHaveBeenCalledWith('/docs', expect.objectContaining({ data: { title: 'a.txt' } }));
  });
});

