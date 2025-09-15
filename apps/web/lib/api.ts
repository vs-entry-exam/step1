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

export interface IngestResponse { indexed: number }

export interface DeleteRequest {
  title: string;
  page?: number;
}

export interface DeleteResponse {
  deleted: number;
}

// Error normalization
export function toErrorMessage(e: any): string {
  return e?.response?.data?.detail ?? e?.message ?? 'Request failed';
}

// API helpers
export async function askQuestion(payload: AskRequest) {
  const { data } = await api.post<AskResponse>('/agent', payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  return data;
}

export async function ingestFiles(files: FileList | File[]): Promise<IngestResponse> {
  const form = new FormData();
  Array.from(files as File[]).forEach((f) => form.append('files', f));
  const { data } = await api.post<IngestResponse>('/rag', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function deleteDocs(payload: DeleteRequest) {
  // Axios supports body on DELETE via the `data` option
  const { data } = await api.delete<DeleteResponse>('/docs', { data: payload, headers: { 'Content-Type': 'application/json' } });
  return data;
}

export async function askAgent(payload: AskRequest): Promise<AskResponse> {
  const { data } = await api.post<AskResponse>('/agent', payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  return data;
}
