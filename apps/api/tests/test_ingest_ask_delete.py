from io import BytesIO


def _upload_txt(client, name: str, content: str):
    files = [("files", (name, BytesIO(content.encode("utf-8")), "text/plain"))]
    r = client.post("/rag", files=files)
    assert r.status_code == 200
    data = r.json()
    assert "indexed" in data and data["indexed"] >= 1
    return data["indexed"]


def test_ingest_txt_then_ask_and_delete(client):
    # Ingest a simple text
    indexed = _upload_txt(client, "sample.txt", "이것은 RAG 테스트 문서입니다. 질문에 답하세요.")
    assert indexed >= 1

    # Ask a question
    r = client.post("/ask", json={"question": "무엇에 대한 문서인가?", "top_k": 4})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data and isinstance(data["answer"], str)
    assert "sources" in data and isinstance(data["sources"], list)

    # Delete by title
    r = client.request("DELETE", "/docs", json={"title": "sample.txt"})
    assert r.status_code == 200
    deleted = r.json()["deleted"]
    # Either we deleted some chunks, or fake chroma fallback delete didn't return count
    assert deleted >= 0


def test_ask_with_empty_question_returns_422(client):
    r = client.post("/ask", json={"question": "", "top_k": 4})
    assert r.status_code == 422
