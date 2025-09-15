from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


def read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_md(path: Path) -> str:
    # For MVP, treat like plain text
    return read_txt(path)


def read_pdf(path: Path) -> List[Tuple[int, str]]:
    from pypdf import PdfReader  # lazy import

    reader = PdfReader(str(path))
    out: List[Tuple[int, str]] = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        out.append((i, text))
    return out


def clean_text(text: str) -> str:
    # Remove extra blank lines and trim
    lines = [ln.strip() for ln in text.splitlines()]
    # Drop leading/trailing empty lines
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    # Collapse multiple empties to single
    cleaned: List[str] = []
    empty = False
    for ln in lines:
        if not ln:
            if not empty:
                cleaned.append("")
            empty = True
        else:
            cleaned.append(ln)
            empty = False
    return "\n".join(cleaned)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    # Simple whitespace-based sliding window
    if not text:
        return []
    words = text.split()
    chunks: List[str] = []
    start = 0
    # Convert approx chars to words by using word count; MVP approach
    window = max(1, chunk_size // 5)
    step = max(1, window - max(0, overlap // 5))
    while start < len(words):
        end = min(len(words), start + window)
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += step
    return chunks

