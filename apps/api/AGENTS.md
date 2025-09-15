# AGENTS.md (API)

역할
- FastAPI 백엔드: 문서 업로드 색인(`/ingest`), 질의(`/ask`), 관리(`/docs`).

실행
- `cd step1/apps/api`
- 가상환경/의존성 설치: `python -m venv .venv && . .venv/Scripts/Activate.ps1 && pip install -r requirements.txt`
- 서버: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

환경 변수(.env.api 주요 항목)
- LLM_PROVIDER: `openai` | `ollama`
- OPENAI_API_KEY, OPENAI_MODEL | OLLAMA_BASE_URL, OLLAMA_MODEL
- EMBEDDING_PROVIDER: `openai` | `ollama`
- OPENAI_EMBEDDING_MODEL | OLLAMA_EMBEDDING_MODEL
- CHROMA_PERSIST_DIR, CHUNK_SIZE, CHUNK_OVERLAP
- ALLOW_ORIGINS

엔드포인트
- GET `/health` → `{ "status": "ok" }`
- POST `/ingest` (multipart) → `{ indexed: number }`
- POST `/ask` (JSON) → `{ answer: string, sources: [{ title, page?, score? }] }`
- DELETE `/docs` (JSON) → `{ deleted: number }`

RAG 파이프라인(요약)
- ingest: PDF/MD/TXT 파싱 → 전처리 → 청크(기본 1000/150) → 임베딩 → Chroma upsert(meta: title, page)
- ask: 임베딩 검색(top_k) → 단일 프롬프트(stuff)로 답변 생성(출처 포함)

테스트
- `python -m pytest -q`

주의
- API 키는 서버 측에만 보관합니다.
- 인덱싱/질의는 동일 임베딩 모델을 사용합니다.
