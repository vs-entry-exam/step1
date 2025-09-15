from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            # Don't overwrite existing environment variables
            if k and (k not in os.environ):
                os.environ[k] = v
    except Exception:
        # Fail silent for env loading; validation happens in Config
        pass


@dataclass
class Config:
    llm_provider: str | None
    openai_api_key: str | None
    openai_model: str | None
    ollama_base_url: str | None
    ollama_model: str | None

    embedding_provider: str | None
    openai_embedding_model: str | None
    ollama_embedding_model: str | None

    chroma_persist_dir: str
    chunk_size: int
    chunk_overlap: int

    allow_origins: List[str]
    prompt_file: Optional[str]


def load_config() -> Config:
    # Load .env.api at the project root (step1/.env.api)
    env_path = Path(__file__).resolve().parents[2] / ".env.api"
    _load_env_file(env_path)

    allow_origins_raw = os.getenv("ALLOW_ORIGINS", "http://localhost:3000")
    allow_origins = [o.strip() for o in allow_origins_raw.split(",") if o.strip()]

    return Config(
        llm_provider=os.getenv("LLM_PROVIDER"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL"),
        ollama_model=os.getenv("OLLAMA_MODEL"),
        embedding_provider=os.getenv("EMBEDDING_PROVIDER"),
        openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL"),
        ollama_embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL"),
        chroma_persist_dir=os.getenv("CHROMA_PERSIST_DIR", "../../chroma"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "150")),
        allow_origins=allow_origins,
        prompt_file=os.getenv("PROMPT_FILE") or os.getenv("PROMPT_PATH"),
    )
