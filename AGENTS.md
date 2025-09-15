# AGENTS.md (Project)

목적: Step1 전체 프로젝트의 목표, 구조, 실행 방법을 한 곳에 요약하고, 세부 내용은 각 범위별 문서로 연결합니다.

참조 문서
- Web: `vision space exam/step1/apps/web/AGENTS.md`
- API: `vision space exam/step1/apps/api/AGENTS.md`

---

### 1) 개요
- 목적: 문서 기반 RAG QA MVP. 업로드한 문서를 인덱싱하고 질문에 한국어로 답하면서 출처(`[title:page]`)를 포함.
- 스택: Next.js(App Router) · FastAPI · LangChain · ChromaDB · OpenAI/Ollama
- 범위: 업로드 → 임베딩/인덱싱 → 검색 → 응답까지 최소 동작 보장.

### 2) 아키텍처
- 프론트엔드(Next.js): `/ingest` 업로드 UI, `/` 질문 UI, Ask/Ingest 토글.
- 백엔드(FastAPI): `/ingest` 파일 수신→파싱·청킹·임베딩→Chroma upsert, `/ask` 검색→LLM 답변 생성.
- 스토리지: ChromaDB 로컬 퍼시스트(`step1/chroma`).
- 프롬프트: `step1/rag/prompts/answer.txt` 정책(컨텍스트 밖은 모른다고 답변, 한국어, 출처 포함).

### 3) 폴더 구조(주요)
```
step1/
├─ apps/
│  ├─ web/         # Next.js 프론트엔드 (Ask/Ingest UI)
│  └─ api/         # FastAPI 백엔드 (/ingest, /ask)
├─ rag/
│  └─ prompts/     # 답변 프롬프트 템플릿
├─ chroma/         # ChromaDB 퍼시스트 디렉터리
├─ data/           # 샘플 문서
├─ .env.api        # 백엔드 환경변수
└─ README.md
```

### 4) 환경 변수
- 백엔드(`step1/.env.api`): LLM/임베딩 제공자(OpenAI|Ollama), 모델명, Chroma 경로, 청킹 설정, CORS.
- 프론트(`step1/apps/web/.env.local`): `NEXT_PUBLIC_API_BASE`(기본 `http://localhost:8000`).

### 5) 실행(로컬)
- 백엔드
  ```bash
  cd "vision space exam/step1/apps/api"
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  # 참고: 반드시 apps/api 디렉터리에서 실행
  # 헬스체크: http://localhost:8000/health → {"status":"ok"}
  ```
- 프론트엔드
  ```bash
  cd "vision space exam/step1/apps/web"
  npm install
  npm run dev
  # 브라우저: http://localhost:3000
  ```

### 6) API 요약
- `GET /health` → `{ "status":"ok" }`
- `POST /ingest` (multipart): 필드 `files`(다중). 응답 `{ indexed: number }`
- `POST /ask` (JSON): `{ question: string, top_k?: number }` → `{ answer: string, sources: [{ title, page?, score? }] }`
  - 상세 계약/내부 로직: `apps/api/AGENTS.md` 참고

### 7) RAG 파이프라인
- 인제스트: PDF/MD/TXT 파싱 → 텍스트 정리 → 청킹(기본 1000/150) → 임베딩 → Chroma upsert(meta: title, page).
- 질의: 질문 임베딩 → 유사도 검색(top_k) → 컨텍스트(stuff) → 프롬프트 → LLM 한국어 응답 → 출처 구성.

### 8) E2E 빠른 테스트
```bash
# 인제스트
cd "vision space exam/step1/apps/api"
curl -F "files=@../../data/sample.pdf" http://localhost:8000/ingest

# 질의
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"sample.pdf 핵심 요약","top_k":4}'
```

### 9) 진행 문서
- 프론트 상세: `vision space exam/step1/apps/web/AGENTS.md`
- 백엔드 상세: `vision space exam/step1/apps/api/AGENTS.md`

---

### 10) 커밋 규칙 (Conventional Commits)
- 형식: `type(scope)!: subject`
  - type: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
  - scope(선택): web, api, rag, prompts, infra, repo 등 폴더/모듈명
  - subject: 한국어/영어 가능, 간결한 명령형 문장, 마침표 X
- 본문(선택): 변경 배경/의도, 주요 변경점 불릿 목록으로 기술(권장 줄바꿈 72자)
- 푸터(선택): 이슈/브레이킹 변경 명시. 예) `Closes #123`, `BREAKING CHANGE: ...`

관찰된 커밋 패턴(최근 로그 기준)과 일관 예시
- `feat(web): Next.js 프론트 초기 세팅 및 기본 페이지 추가`
- `docs(api): 진행상황 요약 추가 (AGENTS.md)`
- `docs: AGENTS.md에 커밋 규칙 추가 (Conventional Commits)`
- `chore: .gitignore 규칙 정리 및 루트로 이동`

가이드
- 범위가 다른 변경은 커밋 분리, 필요한 경우 scope를 붙입니다.
- 사소한 정리/이동/리네이밍은 `chore:`를 사용합니다.
- 문서만 변경은 `docs:`를 사용합니다.
- 호환성 파괴 변경은 `!` 또는 `BREAKING CHANGE:`를 명시합니다.
