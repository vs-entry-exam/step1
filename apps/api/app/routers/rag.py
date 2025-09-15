from __future__ import annotations

from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.rag_service import build_docs, upsert_docs


router = APIRouter()


@router.post("/rag")
async def ingest(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    try:
        blobs = [(f.filename or "untitled", await f.read()) for f in files]
        docs = build_docs(blobs)
        n = upsert_docs(docs)
        return {"indexed": n}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process files: {e}")
