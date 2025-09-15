from __future__ import annotations

from typing import List, Dict, Tuple

from app.models.schemas import AskResponse, SourceItem
from app.core.vectorstore import VectorStore
from app.core.prompts import load_prompt
from app.core.providers.llm import LLMClient


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


def answer_question(question: str, top_k: int = 4) -> AskResponse:
    vs = VectorStore()
    llm = LLMClient()
    result = vs.query(question, top_k=top_k)
    context = build_context(result.documents, result.metadatas)
    if not context:
        return AskResponse(answer="문서에서 답을 찾을 수 없습니다.", sources=[])
    system = load_prompt()
    user = (
        f"Context:\n{context}\n"
        f"Question: {question}\n"
        f"Answer in Korean with citations."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    answer = llm.chat(messages)
    sources: List[SourceItem] = []
    for m, dist in zip(result.metadatas, result.distances):
        score = None
        try:
            score = max(0.0, 1.0 - float(dist))
        except Exception:
            pass
        sources.append(SourceItem(title=m.get("title", ""), page=m.get("page"), score=score))
    return AskResponse(answer=answer.strip(), sources=sources)

