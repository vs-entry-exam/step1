from __future__ import annotations

from typing import Iterable, List

from app.config import load_config


def _ensure_list(texts: Iterable[str]) -> List[str]:
    return [t if isinstance(t, str) else str(t) for t in texts]


class EmbeddingClient:
    """Embedding client backed by LangChain embeddings.

    - openai: langchain_openai.OpenAIEmbeddings
    - ollama: OllamaEmbeddings (langchain_community)
    """

    def __init__(self):
        self.cfg = load_config()
        self.provider = (self.cfg.embedding_provider or "").lower()
        if self.provider == "openai":
            try:
                from langchain_openai import OpenAIEmbeddings  # type: ignore
            except Exception as e:  # pragma: no cover
                raise RuntimeError("LangChain OpenAI integration is required: 'langchain-openai'") from e
            self._emb_cls = OpenAIEmbeddings
            self._model = self.cfg.openai_embedding_model or "text-embedding-3-small"
        elif self.provider == "ollama":
            try:
                from langchain_community.embeddings import OllamaEmbeddings  # type: ignore
            except Exception as e:  # pragma: no cover
                raise RuntimeError("LangChain Ollama embeddings are required: 'langchain-community'") from e
            self._emb_cls = OllamaEmbeddings
            self._model = self.cfg.ollama_embedding_model or "nomic-embed-text"
        else:
            raise ValueError("EMBEDDING_PROVIDER must be 'openai' or 'ollama'")

    def embed(self, texts: Iterable[str]) -> List[List[float]]:
        texts_list = _ensure_list(texts)
        emb = self._emb_cls(model=self._model)
        # LangChain standardizes on embed_documents for batch
        return emb.embed_documents(texts_list)
