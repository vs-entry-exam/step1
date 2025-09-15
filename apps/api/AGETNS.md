# apps/api 진행상황 요약

## 현재 상태
- FastAPI 기본 앱 구성 완료 (`main.py`)
  - `GET /health` 동작, `CORSMiddleware` 설정(`ALLOW_ORIGINS` 기반)
- 설정 로더 구현 (`config.py`)
  - 루트 `step1/.env.api` 로드, LLM/임베딩/Chroma/청크/CORS 설정 지원
- 데이터 모델 정의 (`models.py`)
  - `AskRequest`, `AskResponse`, `SourceItem` 스키마
- 의존성 명시 (`requirements.txt`)
- 문서화 (`README.md`): 설치·환경변수·실행 방법

## 미구현
- `/ingest` 업로드 처리(파싱→청크→임베딩→Chroma upsert)
- `/ask` 질의 처리(Retriever+LLM, 출처 `[title:page]` 포함)
- `rag/ingest`, `rag/prompts` 연동 및 프롬프트 적용

## 파일 구조
- `main.py`: FastAPI 앱, CORS, `/health`
- `config.py`: `.env.api` 로드 및 `Config` 관리
- `models.py`: 요청/응답/출처 스키마
- `requirements.txt`: 필수 패키지 목록
- `README.md`: 셋업/실행 가이드

## 실행
```bash
cd step1/apps/api
python -m venv .venv
# Windows PowerShell: . .venv/Scripts/Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -U pip && pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
헬스체크: `GET http://localhost:8000/health` → `{ "status": "ok" }`

## 다음 작업(TODO)
- `/ingest` 구현: PDF/MD/TXT 파싱 → 전처리 → 청크(`CHUNK_SIZE=1000`, `CHUNK_OVERLAP=150`) → 임베딩 → Chroma upsert(meta: title,page)
- `/ask` 구현: similarity retriever(`top_k`) → stuff 체인 → 한글 답변 + 출처 인용
- `prompts/answer.txt` 적용: “출처 없으면 모른다고 답함” 원칙 준수
- `.env.api` 설정과 실제 사용 모델 일치 확인(인덱싱/질의 동일 임베딩 모델)
- CORS 화이트리스트(`ALLOW_ORIGINS`) 점검

## 참고
- 커밋 규칙: 루트 `AGENTS.md`의 Conventional Commits 요약을 따름
- 개선 여지: `models.py`의 `sources` 기본값은 `Field(default_factory=list)` 사용 권장
