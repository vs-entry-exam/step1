from __future__ import annotations

from fastapi import APIRouter, HTTPException

from models import DeleteRequest, DeleteResponse
from vectorstore import VectorStore


router = APIRouter()


@router.delete("/docs", response_model=DeleteResponse)
async def delete_docs(req: DeleteRequest):
    if not req.title.strip():
        raise HTTPException(status_code=422, detail="title is required")
    vs = VectorStore()
    n = vs.delete_by_meta(req.title, req.page)
    return DeleteResponse(deleted=n)

