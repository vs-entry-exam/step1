import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient


# Ensure apps/api is on sys.path so `import app` works when running tests from repo root
API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


@pytest.fixture(scope="session")
def tmp_chroma_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("chroma")
    return str(d)


@pytest.fixture(autouse=True)
def _set_test_env(tmp_chroma_dir, monkeypatch):
    # Use a temp chroma persistence dir for tests
    monkeypatch.setenv("CHROMA_PERSIST_DIR", tmp_chroma_dir)
    # Avoid accidental real provider use
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")


class _FakeEmbeddingClient:
    def __init__(self):
        pass

    def embed(self, texts):
        # Return a fixed 8-dim vector per text (deterministic by length)
        out = []
        for t in texts:
            n = len(str(t)) % 7 + 1
            vec = [float(n)] * 8
            out.append(vec)
        return out


class _FakeLLMClient:
    def __init__(self):
        pass

    def chat(self, messages, temperature: float = 0.0, max_tokens: int = 256) -> str:
        # Very simple echo that proves wiring
        return "테스트 응답: 출처를 포함하세요."


@pytest.fixture(autouse=True)
def _patch_providers(monkeypatch):
    # Patch providers used by VectorStore and /ask
    import app.core.providers.embeddings as emb_mod
    import app.core.providers.llm as llm_mod

    monkeypatch.setattr(emb_mod, "EmbeddingClient", _FakeEmbeddingClient)
    monkeypatch.setattr(llm_mod, "LLMClient", _FakeLLMClient)
    yield


@pytest.fixture()
def client():
    from app.main import app
    return TestClient(app)

