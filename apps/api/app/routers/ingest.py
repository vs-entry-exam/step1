from __future__ import annotations

from pathlib import Path
import tempfile
from typing import List, Tuple

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import load_config
from app.core.parsing import read_pdf, read_md, read_txt, clean_text, chunk_text
from app.core.vectorstore import VectorStore


router = APIRouter()


@router.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    cfg = load_config()
    vs = VectorStore()

    total_chunks = 0
    docs: List[Tuple[str, int | None, str]] = []

    for f in files:
        suffix = Path(f.filename or "").suffix.lower()
        title = Path(f.filename or "untitled").name
        data = await f.read()
        try:
            if suffix == ".pdf":
                # For PDF, pypdf benefits from a real file path: use secure temp file
                tmp = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tf:
                        tf.write(data)
                        tmp = Path(tf.name)
                    pages = read_pdf(tmp)
                finally:
                    if tmp is not None:
                        try:
                            tmp.unlink(missing_ok=True)
                        except Exception:
                            pass
                for page_num, content in pages:
                    text = clean_text(content)
                    chunks = chunk_text(text, chunk_size=cfg.chunk_size, overlap=cfg.chunk_overlap)
                    for ch in chunks:
                        docs.append((title, page_num, ch))
            elif suffix in {".md", ".txt"}:
                text = (data.decode("utf-8", errors="ignore"))
                text = clean_text(text)
                chunks = chunk_text(text, chunk_size=cfg.chunk_size, overlap=cfg.chunk_overlap)
                for ch in chunks:
                    docs.append((title, None, ch))
                total_chunks += len(chunks)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse {title}: {e}")

    if docs:
        vs.upsert(docs)

    return {"indexed": len(docs)}
