# AGENTS.md (API)

목적: FastAPI 기반 RAG 백엔드의 현재 구현 상태와 사용 방법을 정리합니다.

## 범위
- 디렉터리: `step1/apps/api`
- 역할: 문서 인제스트(임베딩/인덱싱)와 질의 응답(출처 포함) 제공
- 스택: FastAPI · ChromaDB · OpenAI/Ollama 클라이언트 · pypdf

## 상태(현재)
- 앱/CORS/헬스체크: `main.py` (GET `/health` 동작)
- 인제스트 파이프라인: `routes_ingest.py`, `utils_parse.py`, `vectorstore.py`, `providers_embeddings.py`
- 질의 파이프라인: `routes_ask.py`, `providers_llm.py`
- 설정/스키마: `config.py`, `models.py`
// 프롬프트는 코드 내 정책 문자열로 관리합니다.

## 주요 파일
- `main.py`: FastAPI 초기화, CORS, `/health`, 라우터 포함
- `routes_ingest.py`: `POST /ingest` 업로드 → 파싱/클린/청킹 → 임베딩 → Chroma upsert
- `routes_ask.py`: `POST /ask` 유사도 검색 → 컨텍스트 → LLM 답변 생성 → 출처 구성
- `utils_parse.py`: PDF/MD/TXT 읽기, `clean_text`, `chunk_text`
- `providers_embeddings.py`: OpenAI/Ollama 임베딩 클라이언트
- `providers_llm.py`: OpenAI/Ollama LLM 클라이언트
- `vectorstore.py`: Chroma 퍼시스트 초기화, upsert/query
- `config.py`: `.env.api` 로드, 환경 파라미터 제공
- `models.py`: `AskRequest`, `AskResponse`, `SourceItem`

## 환경 변수(`step1/.env.api`)
- LLM: `LLM_PROVIDER=openai|ollama`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- 임베딩: `EMBEDDING_PROVIDER=openai|ollama`, `OPENAI_EMBEDDING_MODEL`, `OLLAMA_EMBEDDING_MODEL`
- RAG: `CHROMA_PERSIST_DIR`, `CHUNK_SIZE`, `CHUNK_OVERLAP`
- CORS: `ALLOW_ORIGINS`

## API 계약
- `GET /health` → `{ "status": "ok" }`
- `POST /ingest` (multipart/form-data)
  - 필드: `files` (다중 파일 허용: PDF/MD/TXT)
  - 응답: `{ "indexed": number }` (업서트된 청크 수)
- `POST /ask` (application/json)
  - 요청: `{ "question": string, "top_k"?: number }`
  - 응답: `{ "answer": string, "sources": [{ "title": string, "page"?: number, "score"?: number }] }`

## 파이프라인 개요
- 인제스트: 파일 파싱 → 텍스트 정리 → 청킹(기본 1000/150) → 임베딩 → Chroma upsert(meta: title, page)
- 질의: 질문 임베딩 → 유사도 검색(top_k) → 컨텍스트(stuff) → 프롬프트 → LLM 한국어 답변 → 출처 구성

## 실행/테스트
```bash
cd step1/apps/api
# (권장) 가상환경 활성화 후 실행
# Windows PowerShell
. .venv/Scripts/Activate.ps1
# macOS/Linux
# source .venv/bin/activate

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 인제스트
curl -F "files=@../../data/sample.pdf" http://localhost:8000/ingest

# 질의
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"sample.pdf 핵심 요약", "top_k":4}'
```

## 비고
- 백엔드는 반드시 `step1/apps/api` 디렉터리에서 실행하세요(임포트 경로 기준).
- 기본값은 OpenAI를 사용합니다. Ollama 사용 시 서버 실행과 모델 pull이 필요합니다.

---

## Refactoring Notes (최근 정리)
- 스키마 기본값 안전화: `AskResponse.sources`를 `Field(default_factory=list)`로 변경해 가변 기본값 이슈 예방. `apps/api/models.py`
- 프롬프트 로딩 정비: `routes_ask.py`에 파일 기반 프롬프트 로더를 함수로 분리(`load_prompt`), mtime 캐시 적용. `.env.api`의 `PROMPT_FILE|PROMPT_PATH`(config 필드 `prompt_file`)로 경로 오버라이드 가능.
- PDF 임시파일 처리: 업로드된 PDF는 `tempfile.NamedTemporaryFile`을 사용해 안전하게 디스크에 기록 후 파싱, 종료 시 삭제. `routes_ingest.py`
- 삭제 API 추가: `DELETE /docs`로 `title`(필수), `page`(선택) 기준 청크 삭제. VectorStore에 `delete_by_meta` 구현(페이지네이션으로 ids 수집 후 일괄 삭제). `routes_admin.py`, `vectorstore.py`
- 설정 일원화: `config.py`에 `prompt_file` 필드 추가, CORS/청킹/모델 설정과 함께 로드.

---

## Tests (백엔드)
- 도구: `pytest`, `fastapi.testclient`
- 위치: `apps/api/tests`
- 실행 예시:
  ```bash
  cd step1/apps/api
  # (권장) 가상환경 활성화 후 테스트 실행
  # Windows PowerShell
  . .venv/Scripts/Activate.ps1
  # macOS/Linux
  # source .venv/bin/activate

  # venv의 pytest를 사용
  python -m pytest -q
  ```
- 구현 내용:
  - `conftest.py`: TestClient 생성, 임시 Chroma 디렉터리 설정, Embedding/LLM 모킹
  - `test_health.py`: `/health` 200 OK
  - `test_ingest_ask_delete.py`: 업로드→질의→삭제 시나리오 검증 및 422 경계 케이스

---

## Code Style (API)
- 포맷터: Black(라인 100), isort(Black 프로파일), Ruff(기본 E/F/I)
- 설정: `apps/api/pyproject.toml`
- 개발 의존성: `apps/api/requirements-dev.txt`
- 실행(venv 활성화 후):
  ```bash
  # 설치(최초 1회)
  pip install -r requirements-dev.txt
  # 포맷/정렬/린트
  black .
  isort .
  ruff check .
  ```

---

## API ����
- `DELETE /docs` (application/json)
  - ��û: `{ "title": string, "page"?: number }`
  - ����: `{ "deleted": number }`

## ����
- ������Ʈ: `.env.api`�� `PROMPT_FILE|PROMPT_PATH`�� ���� ��� ������Ʈ�� ������ �� �ֽ��ϴ�(���� �� mtime ĳ�÷� �ڵ� �ݿ�, ���� �� ���� ��å���� ����).
- �ε��� ���: `CHROMA_PERSIST_DIR` ����δ� `apps/api` �������� �ؼ��˴ϴ�. ������� ������ ����.
