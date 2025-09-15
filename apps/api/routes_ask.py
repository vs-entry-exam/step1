from __future__ import annotations

from pathlib import Path
from typing import List, Dict

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

    # Load prompt template from file with safe fallback
    def _load_prompt() -> str:
        # step1 root = .../apps/api/../../ -> parent[2]
        root = Path(__file__).resolve().parents[2]
        prompt_path = root / "rag" / "prompts" / "answer.txt"
        try:
            return prompt_path.read_text(encoding="utf-8").strip()
        except Exception:
            return (
                "Answer ONLY with the provided context. If missing, say you don't know.\n"
                "Always include Korean answer and cite sources as [title:page]."
            )

    prompt = _load_prompt()
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
