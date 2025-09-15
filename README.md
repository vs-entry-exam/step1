# Step1 · RAG QA MVP

문서 기반 RAG QA 최소 기능을 제공합니다. 업로드한 문서를 색인하고, 웹 UI에서 질문하면 한글 답변과 출처(`[title:page]`)를 함께 반환합니다.

## 개요
- 스택: Next.js(App Router, TypeScript) · FastAPI · LangChain · ChromaDB
- LLM/임베딩: OpenAI 또는 Ollama

## 디렉터리
```
step1/
├─ apps/
│  ├─ web/        # Next.js 프론트
│  └─ api/        # FastAPI 백엔드
├─ rag/
│  └─ prompts/    # 프롬프트 템플릿
├─ chroma/        # ChromaDB 영속 디렉터리
├─ .env.api       # 백엔드 환경변수
└─ README.md
```

## 빠른 시작
백엔드
```
cd step1/apps/api
python -m venv .venv
. .venv/Scripts/Activate.ps1   # Windows
# source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# 헬스체크: http://localhost:8000/health → {"status":"ok"}
```

프론트
```
cd step1/apps/web
npm install
npm run dev -p 3000
# http://localhost:3000
```

## 환경 변수
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

프론트(`step1/apps/web/.env.local`)
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## API 요약
- `GET /health` → `{ "status": "ok" }`
- `POST /ingest` (multipart) → `{ indexed: number }`
- `POST /ask` (JSON) → `{ answer: string, sources: [{ title, page?, score? }] }`
- `DELETE /docs` (JSON) → `{ deleted: number }`

## 로컬 테스트
```
# 업로드(샘플)
cd step1/apps/api
curl -F "files=@../../data/sample.pdf" http://localhost:8000/ingest

# 질의
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"sample.pdf 핵심 요약","top_k":4}'
```

## 체크리스트
- [/ingest] 업로드 후 “indexed: N” 표시
- [/ask] 한글 답변 + [title:page] 출처 포함
- PDF/MD/TXT 각각 1개 이상 동작 확인

## 주의
- 프론트에 API 키를 절대 노출하지 않습니다.
- 인덱싱과 질의에 동일한 임베딩 모델을 사용하세요.
