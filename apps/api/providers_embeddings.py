from __future__ import annotations

from typing import Iterable, List

from config import load_config


def _ensure_list(texts: Iterable[str]) -> List[str]:
    return [t if isinstance(t, str) else str(t) for t in texts]


class EmbeddingClient:
    def __init__(self):
        self.cfg = load_config()
        self.provider = (self.cfg.embedding_provider or "").lower()
        if self.provider == "openai":
            try:
                from openai import OpenAI  # type: ignore
            except Exception as e:  # pragma: no cover - import error surfaces at runtime
                raise RuntimeError("openai package is required for OpenAI embeddings") from e
            self._openai = OpenAI()
            self._openai_model = self.cfg.openai_embedding_model or "text-embedding-3-small"
        elif self.provider == "ollama":
            try:
                import ollama  # type: ignore
            except Exception as e:  # pragma: no cover
                raise RuntimeError("ollama package is required for Ollama embeddings") from e
            self._ollama = ollama
            self._ollama_model = self.cfg.ollama_embedding_model or "nomic-embed-text"
        else:
            raise ValueError("EMBEDDING_PROVIDER must be 'openai' or 'ollama'")

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        texts_list = _ensure_list(texts)
        if self.provider == "openai":
            resp = self._openai.embeddings.create(model=self._openai_model, input=texts_list)
            return [d.embedding for d in resp.data]
        else:  # ollama
            # ollama.embeddings does not support batching in one call; loop
            out: List[List[float]] = []
            for t in texts_list:
                r = self._ollama.embeddings(model=self._ollama_model, prompt=t)
                out.append(r["embedding"])  # type: ignore[index]
            return out

