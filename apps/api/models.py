from pydantic import BaseModel, Field
from typing import List, Optional


class SourceItem(BaseModel):
    title: str
    page: Optional[int] = None
    score: Optional[float] = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=4, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceItem] = []


class DeleteRequest(BaseModel):
    title: str
    page: Optional[int] = None


class DeleteResponse(BaseModel):
    deleted: int
