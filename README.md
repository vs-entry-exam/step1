# Step1 — RAG QA MVP

문서 기반 RAG QA 최소 기능(MVP)을 구현한 프로젝트입니다. 업로드한 문서(PDF/MD/TXT)를 인덱싱하고, 질문에 대해 출처를 포함한 한국어 답변을 제공합니다.

## 개요
- 스택: Next.js(App Router, TypeScript) · FastAPI · LangChain · ChromaDB
- LLM/임베딩: OpenAI 또는 Ollama(서로 교체 가능)
- 목표: 업로드 → 임베딩/인덱싱 → 유사도 검색 → LLM 응답(출처 포함)

## 주요 기능(MVP)
- 인제스트(`/ingest`): 여러 문서 업로드 → 파싱/클린/청킹 → 임베딩 → Chroma upsert → `indexed: N`
- 질의(`/ask`): 질문 + `top_k` → 유사도 검색 → 한국어 답변 + 출처(`[title:page]`)
- 프론트 헤더 토글: Ask ↔ Ingest 페이지 전환

## 폴더 구조(주요)
```
step1/
├─ apps/
│  ├─ web/            # Next.js 프론트엔드
│  └─ api/            # FastAPI 백엔드
├─ rag/
│  └─ prompts/        # 답변 프롬프트 템플릿
├─ chroma/            # ChromaDB 퍼시스트 디렉터리
├─ data/              # 샘플 문서
├─ .env.api           # 백엔드 환경변수
└─ README.md
```

## 빠른 시작
프론트엔드
```
cd "vision space exam/step1/apps/web"
npm install
npm run dev -p 3000
# 브라우저: http://localhost:3000
```

백엔드
```
cd "vision space exam/step1/apps/api"
python -m venv .venv
. .venv/Scripts/Activate.ps1   # Windows PowerShell
# source .venv/bin/activate    # macOS/Linux
python -m pip install -U pip
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# 헬스체크: http://localhost:8000/health → {"status":"ok"}

참고: 백엔드는 반드시 `vision space exam/step1/apps/api` 디렉터리에서 실행하세요. 임포트 경로 기준으로 실행되며, 다른 위치에서 실행하면 모듈 임포트 오류가 발생할 수 있습니다.
```

### 빠른 실행 스크립트(의존성 설치 완료 시)
이미 가상환경 생성 및 `pip install -r requirements.txt`, 프론트의 `npm install`까지 끝난 상태라면, 루트 스크립트로 손쉽게 실행할 수 있습니다.

PowerShell에서:
```
cd "vision space exam/step1"

# 백엔드와 프론트 동시에(각각 새 터미널 창)
# Windows PowerShell 내에서:
powershell -File .\scripts\dev.ps1 -All
# 또는 현재 세션에서 실행:
./scripts/dev.ps1 -All

# 백엔드만
powershell -File .\scripts\dev.ps1 -Backend
# 또는
./scripts/dev.ps1 -Backend

# 프론트만
powershell -File .\scripts\dev.ps1 -Frontend
# 또는
./scripts/dev.ps1 -Frontend
```

주의: 실행 정책 오류가 나면 현재 세션 한정으로 허용하세요.
```
Set-ExecutionPolicy -Scope Process RemoteSigned
```

## 환경변수
백엔드(`step1/.env.api`)
```
LLM_PROVIDER=openai            # openai | ollama
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
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

프론트엔드(`step1/apps/web/.env.local`)
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## 백엔드 API
- `GET /health` → `{ "status": "ok" }`
- `POST /ingest` (multipart/form-data)
  - 필드: `files` (파일 다중 허용)
  - 응답: `{ "indexed": number }`
- `POST /ask` (application/json)
  - 요청: `{ "question": string, "top_k"?: number }`
  - 응답: `{ "answer": string, "sources": [{ "title": string, "page"?: number, "score"?: number }] }`

## 프론트엔드 UI
- `/ingest`: 파일 선택·업로드 → 인덱싱 결과(`indexed: N`)와 에러/로딩 표시
- `/`: 질문·`top_k` 입력 → 답변과 출처 리스트(`[title:page]`, score는 소수 3자리 표시)
- 헤더: Ask ↔ Ingest 토글 버튼

## RAG 파이프라인
- 인제스트: PDF(pypdf)/MD/TXT → 텍스트 클린 → 청킹(기본 1000/150) → 임베딩 → Chroma upsert(meta: title, page)
- 질의: 질문 임베딩 → 유사도 검색(top_k) → 컨텍스트(stuff) → 프롬프트 → LLM 한국어 응답 → 출처 구성

## E2E 테스트 방법
인제스트(cURL)
```
cd "vision space exam/step1/apps/api"
curl -F "files=@../../data/sample.pdf" http://localhost:8000/ingest
```

질의(cURL)
```
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"sample.pdf 핵심 요약","top_k":4}'
```

프론트에서 동일 흐름 실행 후 답변과 출처가 표시되는지 확인합니다.
