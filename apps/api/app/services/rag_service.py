from __future__ import annotations

from pathlib import Path
import tempfile
from typing import List, Optional, Tuple

from app.config import load_config
from app.core.parsing import read_pdf, read_md, read_txt, clean_text, chunk_text
from app.core.vectorstore import VectorStore


Doc = Tuple[str, Optional[int], str]  # (title, page, chunk)


def build_docs(files: List[Tuple[str, bytes]]) -> List[Doc]:
    """Parse uploaded files and return chunks with metadata.

    files: list of (filename, data)
    """
    cfg = load_config()
    out: List[Doc] = []
    for filename, data in files:
        title = Path(filename or "untitled").name
        suffix = Path(filename or "").suffix.lower()
        if suffix == ".pdf":
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
                    out.append((title, page_num, ch))
        elif suffix in {".md", ".txt"}:
            text = data.decode("utf-8", errors="ignore")
            text = clean_text(text)
            chunks = chunk_text(text, chunk_size=cfg.chunk_size, overlap=cfg.chunk_overlap)
            for ch in chunks:
                out.append((title, None, ch))
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    return out


def upsert_docs(docs: List[Doc]) -> int:
    if not docs:
        return 0
    vs = VectorStore()
    vs.upsert(docs)
    return len(docs)

