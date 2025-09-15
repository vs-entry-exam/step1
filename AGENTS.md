## ✅ AGENTS.md

> **목표**: 업로드한 문서를 RAG로 색인하고, 웹 UI에서 질의하면 출처를 포함해 답한다.
> **스택**: Next.js(프론트) · FastAPI(백엔드) · LangChain(RAG) · ChromaDB(로컬) · LLM(OpenAI 또는 Ollama)

### 0) 사용자 시나리오

1. `/ingest` 에서 PDF/MD/TXT 업로드
2. 백엔드가 파싱→청크→임베딩→Chroma upsert
3. `/` 에서 질문 입력
4. Retriever로 문서 검색 → LLM이 **출처 인용** 포함 답변

---

### 1) 디렉터리

```
step1/
├─ apps/
│  ├─ web/        # Next.js (App Router) 프론트
│  └─ api/        # FastAPI 백엔드
├─ rag/
│  ├─ ingest/     # 파서·청크·임베딩
│  └─ prompts/    # 프롬프트 템플릿
├─ chroma/        # ChromaDB 영속 디렉터리
├─ data/          # 샘플 문서
├─ .env.api       # 백엔드 환경변수
├─ .env.web       # 프론트 환경변수
└─ README.md
```

---

### 2) 환경 셋업 (최소)

**백엔드**

```bash
cd step1/apps/api
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install fastapi uvicorn[standard] langchain chromadb pypdf python-multipart
# OpenAI 사용 시
pip install openai tiktoken
# Ollama 사용 시
pip install ollama
```

`.env.api`

```
LLM_PROVIDER=openai            # openai | ollama
OPENAI_API_KEY=sk-...          # (openai 시)
OPENAI_MODEL=gpt-4o-mini       # 예시
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

EMBEDDING_PROVIDER=openai      # openai | ollama
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

CHROMA_PERSIST_DIR=../../chroma
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
ALLOW_ORIGINS=http://localhost:3000
```

실행:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**프론트**

```bash
cd step1/apps/web
npm create next-app@latest . -- --ts
npm i axios
echo "NEXT_PUBLIC_API_BASE=http://localhost:8000" > .env.web
npm run dev -p 3000
```

---

### 3) API (MVP 고정형)

* `GET /health` → `{ "status":"ok" }`
* `POST /ingest` (multipart/form-data)

  * 다중 파일 업로드 → 파싱·청크·임베딩·upsert
  * 응답: `{ "indexed": 3 }`
* `POST /ask` (JSON)

  ```json
  { "question": "문서 요약", "top_k": 4 }
  ```

  응답:

  ```json
  {
    "answer": "요약 내용...",
    "sources": [
      {"title":"file.pdf","page":3,"score":0.82}
    ]
  }
  ```

---

### 4) RAG 파이프라인(최소 구현)

**ingest**

1. 파일 수신(PDF: `pypdf`; MD/TXT: 기본 파서)
2. 전처리(빈줄/머리말·꼬리말 단순 제거)
3. 청크: `CHUNK_SIZE=1000`, `OVERLAP=150`
4. 임베딩 → Chroma upsert(meta: title, page)

**ask**

1. Retriever(similarity, `top_k`)
2. **stuff** 체인 + 단일 프롬프트
3. “출처 없으면 모른다고 답함” 원칙

`prompts/answer.txt` (예)

```
Answer ONLY with the provided context. If missing, say you don't know.
Always include Korean answer and cite sources as [title:page].
```

---

### 5) 프론트(UI 최소)

* `/ingest`: 파일 선택 → 업로드 버튼 → “indexed: N” 표시
* `/`: 질문 입력 → 응답 텍스트 박스 + **출처 토글**(title\:page 목록)

---

### 6) 보안·운영(필수만)

* 프론트에 API 키 노출 금지(키는 백엔드 .env.api에만)
* CORS: `ALLOW_ORIGINS` 화이트리스트
* 동일 임베딩 모델로 **인덱싱과 질의** 수행

---

### 7) 로컬 테스트

```bash
# 백엔드
cd step1/apps/api && uvicorn main:app --reload
# 프론트
cd step1/apps/web && npm run dev -p 3000
# 샘플 업로드
curl -F "files=@../../data/sample.pdf" http://localhost:8000/ingest
# 질의
curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question":"sample.pdf 핵심 요약", "top_k":4}'
```

---

### 8) 제출 체크리스트

* [ ] `/ingest` 업로드 후 “indexed: N” 표시
* [ ] `/ask` 응답에 **한글 답변 + \[title\:page] 출처** 포함
* [ ] 샘플 PDF/MD/TXT 각각 1개 이상으로 동작 확인
* [ ] 실행/시연 영상(업로드→질의→출처 확인 흐름)

---

### 9) 커밋 규칙 (Conventional Commits, 요약)

- 형식: `type(scope)!: subject`
  - `type`: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
  - `scope`(선택): `web`, `api`, `rag`, `ingest`, `prompts`, `infra`, `repo` 등 디렉터리/모듈명
  - `subject`: 한글/영문 모두 가능, 간결한 현재형 설명(마침표 X)
- 본문(선택): 변경 배경과 상세를 `- ` 불릿으로 기술, 줄바꿈 72자 권장
- 푸터(선택): `Closes #123`, `BREAKING CHANGE:` 등 표기
- 메시지 언어는 한국어 권장(일관성 유지)

예시(현재 히스토리 기준):

```
feat(web): Next.js 프론트 초기 세팅 및 기본 페이지 추가
chore: update AGENTS.md
docs: README 업데이트
```

가이드:

- 여러 영역이 섞이면 커밋을 분리하거나, 대표 scope를 쓰고 본문에 상세를 불릿으로 정리
- 사소한 정리/설정 변경은 `chore:` 사용
- 문서만 변경은 `docs:` 사용 (예: 과거 `Create README.md` → `docs: create README` 권장)
- 파급적 변경은 `!`와 `BREAKING CHANGE:`로 명시
