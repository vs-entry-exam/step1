from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import AskRequest, AskResponse
from app.services.ask_service import answer_question


router = APIRouter()


@router.post("/agent", response_model=AskResponse)
async def agent_endpoint(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=422, detail="question is required")
    # 통합 QA 경로: 서비스 레이어를 사용하여 컨텍스트/프롬프트/LLM 호출과 sources 구성까지 수행
    return answer_question(req.question, top_k=req.top_k)

