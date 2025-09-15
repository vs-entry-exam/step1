from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from app.config import load_config

_PROMPT_CACHE: Optional[dict] = None


def project_root() -> Path:
    # this file: apps/api/app/core/prompts.py → step1 root is parents[4]
    return Path(__file__).resolve().parents[4]


def resolve_prompt_path() -> Path:
    cfg = load_config()
    env_path = cfg.prompt_file or os.getenv("PROMPT_FILE") or os.getenv("PROMPT_PATH")
    root = project_root()
    if env_path:
        p = Path(env_path)
        if not p.is_absolute():
            p = (root / p).resolve()
        return p
    return root / "rag" / "prompts" / "answer.txt"


def load_prompt() -> str:
    global _PROMPT_CACHE
    p = resolve_prompt_path()
    try:
        stat = p.stat()
        mtime = stat.st_mtime
        if _PROMPT_CACHE and _PROMPT_CACHE.get("path") == str(p) and _PROMPT_CACHE.get("mtime") == mtime:
            return _PROMPT_CACHE["content"]  # type: ignore[index]
        content = p.read_text(encoding="utf-8").strip()
        _PROMPT_CACHE = {"path": str(p), "mtime": mtime, "content": content}
        return content
    except Exception:
        return (
            "Answer ONLY with the provided context. If missing, say you don't know.\n"
            "Always include Korean answer and cite sources as [title:page]."
        )

