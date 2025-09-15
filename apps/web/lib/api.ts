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

