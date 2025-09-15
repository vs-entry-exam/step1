from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import load_config
from app.models.schemas import AskRequest, AskResponse
from app.core.vectorstore import VectorStore


router = APIRouter()


def _make_retrieval_tool(top_k: int = 4):
    # Lazy imports to avoid importing langchain at module import if not needed
    try:
        from langchain.tools import Tool  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError("langchain.tools is required") from e

    vs = VectorStore()

    def _retrieve(q: str) -> str:
        res = vs.query(q, top_k=top_k)
        lines = []
        for doc, meta in zip(res.documents, res.metadatas):
            title = meta.get("title", "")
            page = meta.get("page")
            header = f"[source: {title}{':' + str(page) if page is not None else ''}]"
            lines.append(header + "\n" + doc)
        return "\n\n".join(lines)

    return Tool(
        name="retrieval",
        func=_retrieve,
        description="Use this to retrieve relevant context from the indexed documents. Input is the user question. Output is concatenated context with [source:title:page] headers.",
    )


@router.post("/agent", response_model=AskResponse)
async def agent_endpoint(req: AskRequest):
    cfg = load_config()
    if (cfg.llm_provider or "openai").lower() != "openai":
        # For MVP, the LangChain agent is wired with OpenAI chat model only
        raise HTTPException(status_code=400, detail="Agent mode currently supports LLM_PROVIDER=openai only")

    try:
        from langchain_openai import ChatOpenAI  # type: ignore
        from langchain.agents import initialize_agent, AgentType  # type: ignore
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"LangChain/OpenAI packages not available: {e}")

    if not req.question.strip():
        raise HTTPException(status_code=422, detail="question is required")

    tool = _make_retrieval_tool(top_k=req.top_k)

    llm = ChatOpenAI(
        model=cfg.openai_model or "gpt-4o-mini",
        temperature=0,
        max_tokens=800,
    )

    agent = initialize_agent(
        tools=[tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
    )

    # Execute agent with the user question
    answer_text = agent.invoke({"input": req.question})  # type: ignore
    if isinstance(answer_text, dict) and "output" in answer_text:
        answer = str(answer_text["output"])  # type: ignore[index]
    else:
        answer = str(answer_text)

    # Replace default agent stop message with a user-friendly Korean fallback
    stop_msg = "Agent stopped due to iteration limit or time limit."
    if not answer.strip() or stop_msg in answer:
        answer = "해당 정보를 문서에서 찾을 수 없습니다."

    return AskResponse(answer=answer.strip(), sources=[])
