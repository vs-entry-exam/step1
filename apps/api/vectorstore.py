from __future__ import annotations

from dataclasses import dataclass
from hashlib import md5
from pathlib import Path
from typing import List, Dict, Any, Tuple

from config import load_config
from providers_embeddings import EmbeddingClient


def _persist_dir(base: str) -> str:
    p = Path(base)
    if not p.is_absolute():
        p = (Path(__file__).resolve().parent / p).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


@dataclass
class VSResult:
    documents: List[str]
    metadatas: List[Dict[str, Any]]
    distances: List[float]


class VectorStore:
    def __init__(self, collection: str = "docs"):
        self.cfg = load_config()
        self.embedder = EmbeddingClient()

        try:
            import chromadb  # type: ignore
            from chromadb.config import Settings  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("chromadb package is required") from e

        persist = _persist_dir(self.cfg.chroma_persist_dir)
        try:
            # Newer Chroma
            from chromadb import PersistentClient  # type: ignore

            self.client = PersistentClient(path=persist)
            self.collection = self.client.get_or_create_collection(name=collection)
        except Exception:
            # Fallback to legacy Settings API
            self.client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist))
            self.collection = self.client.get_or_create_collection(name=collection)

    def _make_id(self, title: str, page: int | None, content: str) -> str:
        h = md5(content.encode("utf-8")).hexdigest()[:16]
        return f"{title}:{page if page is not None else 0}:{h}"

    def upsert(self, docs: List[Tuple[str, int | None, str]]):
        if not docs:
            return 0
        texts = [c for (_, _, c) in docs]
        embeddings = self.embedder.embed(texts)
        ids = [self._make_id(t, p, c) for (t, p, c) in docs]
        metadatas = [{"title": t, "page": p} for (t, p, _) in docs]
        self.collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=texts)
        return len(docs)

    def query(self, question: str, top_k: int = 4) -> VSResult:
        q_emb = self.embedder.embed([question])[0]
        out = self.collection.query(query_embeddings=[q_emb], n_results=top_k)
        # Chroma returns lists per query; unwrap the first
        documents = (out.get("documents") or [[]])[0]
        metadatas = (out.get("metadatas") or [[]])[0]
        distances = (out.get("distances") or [[]])[0]
        return VSResult(documents=documents, metadatas=metadatas, distances=distances)

    def delete_by_meta(self, title: str, page: int | None = None) -> int:
        where = {"title": title}
        if page is not None:
            where["page"] = page
        # Fetch matching ids with pagination (some versions of Chroma apply a default limit)
        all_ids: list[str] = []
        offset = 0
        limit = 1000
        try:
            while True:
                got = self.collection.get(  # type: ignore[attr-defined]
                    where=where,
                    include=["metadatas"],  # keep payload small; ids are always included
                    limit=limit,
                    offset=offset,
                )
                ids = got.get("ids") or []
                if not ids:
                    break
                all_ids.extend(ids)
                offset += len(ids)
            if all_ids:
                self.collection.delete(ids=all_ids)
            else:
                # As a fallback, attempt where-based delete anyway
                self.collection.delete(where=where)
            return len(all_ids)
        except Exception:
            try:
                self.collection.delete(where=where)
            except Exception:
                pass
            return 0

    def delete_all(self) -> None:
        # Drop and recreate the collection
        name = getattr(self.collection, "name", "docs")
        try:
            self.client.delete_collection(name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(name=name)
