import axios from 'axios';

const baseURL = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export const api = axios.create({ baseURL, timeout: 60_000 });

export interface SourceItem {
  title: string;
  page?: number;
  score?: number;
}

export interface AskRequest {
  question: string;
  top_k?: number;
}

export interface AskResponse {
  answer: string;
  sources: SourceItem[];
}

export interface DeleteRequest {
  title: string;
  page?: number;
}

export interface DeleteResponse {
  deleted: number;
}

export async function deleteDocs(payload: DeleteRequest) {
  // Axios supports body on DELETE via the `data` option
  const { data } = await api.delete<DeleteResponse>('/docs', { data: payload, headers: { 'Content-Type': 'application/json' } });
  return data;
}
