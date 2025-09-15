from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Optional

from fastapi import APIRouter, HTTPException

from config import load_config
from models import AskRequest, AskResponse, SourceItem
from providers_llm import LLMClient
from vectorstore import VectorStore


router = APIRouter()


def build_context(docs: List[str], metas: List[Dict], max_chars: int = 4000) -> str:
    parts: List[str] = []
    total = 0
    for i, (d, m) in enumerate(zip(docs, metas), start=1):
        title = m.get("title", "")
        page = m.get("page")
        head = f"[Source {i} - {title}{':' + str(page) if page is not None else ''}]\n"
        body = d.strip()
        segment = head + body + "\n\n"
        if total + len(segment) > max_chars:
            break
        parts.append(segment)
        total += len(segment)
    return "".join(parts)


# Prompt loading with simple mtime-based cache
_PROMPT_CACHE: Optional[dict] = None


def _project_root() -> Path:
    # step1 root = .../apps/api/../../ -> parent[2]
    return Path(__file__).resolve().parents[2]


def _resolve_prompt_path() -> Path:
    # Allow override via config (PROMPT_FILE/PROMPT_PATH) or environment variables
    cfg = load_config()
    env_path = cfg.prompt_file or os.getenv("PROMPT_FILE") or os.getenv("PROMPT_PATH")
    root = _project_root()
    if env_path:
        p = Path(env_path)
        if not p.is_absolute():
            p = (root / p).resolve()
        return p
    return root / "rag" / "prompts" / "answer.txt"


def load_prompt() -> str:
    global _PROMPT_CACHE
    p = _resolve_prompt_path()
    try:
        stat = p.stat()
        mtime = stat.st_mtime
        if _PROMPT_CACHE and _PROMPT_CACHE.get("path") == str(p) and _PROMPT_CACHE.get("mtime") == mtime:
            return _PROMPT_CACHE["content"]  # type: ignore[index]
        content = p.read_text(encoding="utf-8").strip()
        _PROMPT_CACHE = {"path": str(p), "mtime": mtime, "content": content}
        return content
    except Exception:
        # Safe fallback if file missing or unreadable
        return (
            "Answer ONLY with the provided context. If missing, say you don't know.\n"
            "Always include Korean answer and cite sources as [title:page]."
        )


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=422, detail="question is required")

    cfg = load_config()
    vs = VectorStore()
    llm = LLMClient()

    result = vs.query(req.question, top_k=req.top_k)
    context = build_context(result.documents, result.metadatas)
    if not context:
        # No context found; follow prompt policy
        return AskResponse(answer="문서에서 답을 찾을 수 없습니다.", sources=[])

    # Load prompt (file-based with caching; falls back to default policy)
    prompt = load_prompt()
    # messages
    system = prompt
    user = (
        f"Context:\n{context}\n"
        f"Question: {req.question}\n"
        f"Answer in Korean with citations."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    answer = llm.chat(messages)

    # Build sources list
    sources: List[SourceItem] = []
    for m, dist in zip(result.metadatas, result.distances):
        score = None
        try:
            # In cosine distance, smaller is better; convert to similarity-ish
            score = max(0.0, 1.0 - float(dist))
        except Exception:
            pass
        sources.append(SourceItem(title=m.get("title", ""), page=m.get("page"), score=score))

    return AskResponse(answer=answer.strip(), sources=sources)
