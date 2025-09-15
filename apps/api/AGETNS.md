# apps/api 진행상황 요약 (최신)

- 업데이트 시각(UTC): 2025-09-15 06:43:42Z

## 현재 상태
- FastAPI 앱 구성 및 CORS 설정 완료 (`main.py`)
  - `GET /health` 동작
  - `routes_ingest`, `routes_ask` 라우터 포함(try/except로 초기 스캐폴딩 대응)
- 인제스트 파이프라인 구현 (`routes_ingest.py`, `utils_parse.py`, `vectorstore.py`, `providers_embeddings.py`)
  - 지원 포맷: PDF(pypdf), MD/TXT(텍스트 처리)
  - 전처리: 빈줄 정리(`clean_text`), 슬라이딩 윈도우 청크(`chunk_text`)
  - 임베딩: OpenAI/Ollama 스위치 가능(`EMBEDDING_PROVIDER`), 배치/반복 처리
  - VectorStore: ChromaDB 영속 클라이언트 사용, upsert/query 제공
- 질의 파이프라인 구현 (`routes_ask.py`, `providers_llm.py`)
  - Retriever: Chroma similarity로 top-k 문서 조회
  - LLM: OpenAI/Ollama 전환 가능(`LLM_PROVIDER`), 단일 stuff 프롬프트로 답변 생성
  - 답변 원칙: 컨텍스트 기반, 부족 시 “모른다” 대응, 출처 `[title:page]` 포함
- 설정 관리 (`config.py`): `step1/.env.api` 로드, CORS/모델/임베딩/청크 등
- 모델 (`models.py`): `AskRequest`, `AskResponse`, `SourceItem`
- 의존성 (`requirements.txt`), 사용법 문서 (`README.md`)

## 최근 변경 하이라이트
- 신규 모듈 추가: `providers_embeddings.py`, `providers_llm.py`, `vectorstore.py`, `utils_parse.py`, `routes_ingest.py`, `routes_ask.py`
- `main.py`에 라우터 포함 로직 추가
- 인제스트/질의 엔드포인트 동작 수준으로 스캐폴딩 완료

## 파일 구조(요약)
- `main.py`: 앱 초기화, CORS, 라우터 포함, `/health`
- `routes_ingest.py`: `POST /ingest` 업로드→파싱→청크→임베딩→Chroma upsert
- `routes_ask.py`: `POST /ask` 검색→프롬프트→답변+출처
- `utils_parse.py`: PDF/MD/TXT 파서, 전처리, 청크
- `providers_embeddings.py`: OpenAI/Ollama 임베딩 클라이언트
- `providers_llm.py`: OpenAI/Ollama LLM 클라이언트
- `vectorstore.py`: Chroma 영속 클라이언트, upsert/query
- `config.py`, `models.py`, `requirements.txt`, `README.md`

## 실행/테스트
```bash
cd step1/apps/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 업로드
curl -F "files=@../../data/sample.pdf" http://localhost:8000/ingest
# 질의
curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question":"sample.pdf 핵심 요약", "top_k":4}'
```

## 주의 및 개선 포인트
- 임시 파일: PDF 파싱 시 현재 작업 디렉터리에 임시 저장 후 삭제 → `tempfile` 사용으로 개선 권장
- `models.py`: `sources` 기본값은 가변 객체 → `Field(default_factory=list)` 권장
- `.venv` 등 가상환경 파일이 트래킹 대상에 보임 → `.gitignore` 패턴 확인/보완 필요
- 인덱싱/질의에 동일 임베딩 모델 사용(설정 일관성 확인)
