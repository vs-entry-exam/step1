# AGENTS.md (API)

목적: FastAPI 기반 RAG 백엔드의 구현 상태와 사용 방법을 정리합니다.

## 범위
- 디렉터리: `step1/apps/api`
- 역할: 문서 업로드(인덱싱)와 질의 응답(출처 포함) 제공
- 스택: FastAPI · ChromaDB · OpenAI/Ollama 클라이언트 · pypdf

## 현재 상태
- 앱/CORS/헬스체크: `app/main.py` (GET `/health` 동작)
- 업로드 파이프라인: `app/routers/ingest.py`, `app/core/parsing.py`, `app/core/vectorstore.py`, `app/core/providers/embeddings.py`
- 질의 파이프라인: `app/routers/ask.py`, `app/core/providers/llm.py`, `app/core/prompts.py`
- 설정/스키마: `app/config.py`, `app/models/schemas.py`

## 주요 파일
- `app/main.py`: FastAPI 초기화, CORS, `/health`, 라우터 포함
- `app/routers/ingest.py`: `POST /ingest` 업로드 → 파싱/클린/청킹 → 임베딩 → Chroma upsert
- `app/routers/ask.py`: `POST /ask` 유사도 검색 → 컨텍스트 → LLM 답변 생성 → 출처 구성
- `app/routers/admin.py`: `DELETE /docs` 메타(title/page) 기반 삭제
- `app/core/vectorstore.py`: Chroma 퍼시스트 초기화, upsert/query/delete
- `app/core/parsing.py`: PDF/MD/TXT 읽기, `clean_text`, `chunk_text`
- `app/core/providers/*`: 임베딩/LLM 클라이언트(OpenAI/Ollama)
- `app/core/prompts.py`: 프롬프트 파일 로더(mtime 캐시, 폴백 포함)
- `app/config.py`: `.env.api` 로드, `prompt_file` 등 환경 파라미터 제공

## 환경 변수(`step1/.env.api`)
- LLM: `LLM_PROVIDER=openai|ollama`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- 임베딩: `EMBEDDING_PROVIDER=openai|ollama`, `OPENAI_EMBEDDING_MODEL`, `OLLAMA_EMBEDDING_MODEL`
- RAG: `CHROMA_PERSIST_DIR`(상대경로는 `apps/api` 기준), `CHUNK_SIZE`, `CHUNK_OVERLAP`
- CORS: `ALLOW_ORIGINS`
- 프롬프트: `PROMPT_FILE` 또는 `PROMPT_PATH`로 파일 경로 오버라이드(미지정/실패 시 내장 정책 사용)

## API 계약
- `GET /health` → `{ "status": "ok" }`
- `POST /ingest` (multipart/form-data)
  - 필드: `files` (다중 허용: PDF/MD/TXT)
  - 응답: `{ "indexed": number }`
- `POST /ask` (application/json)
  - 요청: `{ "question": string, "top_k"?: number }`
  - 응답: `{ "answer": string, "sources": [{ "title": string, "page"?: number, "score"?: number }] }`
- `DELETE /docs` (application/json)
  - 요청: `{ "title": string, "page"?: number }`
  - 응답: `{ "deleted": number }`

## RAG 파이프라인
- 업로드: 파일 파싱 → 텍스트 정리 → 청킹(기본 1000/150) → 임베딩 → Chroma upsert(meta: title, page)
- 질의: 질문 임베딩 → 유사도 검색(top_k) → 컨텍스트(stuff) → 프롬프트 → LLM 한국어 답변 → 출처 구성

## 실행/테스트
```
cd step1/apps/api
# (권장) 가상환경 활성화
. .venv/Scripts/Activate.ps1  # Windows
# source .venv/bin/activate   # macOS/Linux

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 업로드 예시
curl -F "files=@../../data/sample.pdf" http://localhost:8000/ingest

# 질의 예시
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"sample.pdf 핵심 요약", "top_k":4}'

# 테스트(pytest)
python -m pytest -q
```

## Code Style (API)
- 포맷터: Black(라인 100)
- 임포트 정렬: isort(Black 프로파일, from-first)
- 린터: Ruff(E/F/I)
- 설정: `apps/api/pyproject.toml`
- 설치/실행(venv):
```
pip install -r requirements-dev.txt
isort . && black . && ruff check . --fix
```
