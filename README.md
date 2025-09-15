# Step1 — RAG QA MVP

문서 기반 RAG QA 최소 기능(MVP) 프로젝트입니다. 업로드한 문서(PDF/MD/TXT)를 인덱싱하고, 질문에 대해 한국어 답변과 출처(`[title:page]`)를 제공합니다.

## 개요
- 스택: Next.js(App Router, TypeScript) · FastAPI · LangChain · ChromaDB
- LLM/임베딩: OpenAI 또는 Ollama(교체 가능)

## 폴더 구조(요약)
```
step1/
├─ apps/
│  ├─ web/         # Next.js 프론트엔드(Ask/Upload)
│  └─ api/         # FastAPI 백엔드(app 패키지)
├─ chroma/         # ChromaDB 퍼시스트 디렉터리
├─ data/           # 샘플 문서
├─ .env.api        # 백엔드 환경변수
└─ README.md
```

## 다이어그램
<img width="3924" height="2564" alt="image" src="https://github.com/user-attachments/assets/6d86bf51-63c8-4788-90e9-383c37229e31" />

## 시연 동영상
[youtube_link](https://youtu.be/r_hEyD05s1g?si=57VyQhA3NnOT8N9)

## 빠른 시작
백엔드
```
cd "vision space exam/step1/apps/api"
python -m venv .venv
. .venv/Scripts/Activate.ps1   # Windows
# source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# 헬스체크: http://localhost:8000/health → {"status":"ok"}
```

프론트엔드
```
cd "vision space exam/step1/apps/web"
npm install
npm run dev
# http://localhost:3000
```

## 스크립트로 실행(의존성 설치 완료 시)
루트 스크립트로 백엔드/프론트를 손쉽게 실행할 수 있습니다.

Windows PowerShell
```
cd "vision space exam/step1"
# 백엔드와 프론트 동시에(각각 새 터미널 창)
powershell -File .\scripts\dev.ps1 -All
# 백엔드만 / 프론트만
powershell -File .\scripts\dev.ps1 -Backend
powershell -File .\scripts\dev.ps1 -Frontend

# 실행 정책 오류 시(현재 세션 한정 허용)
Set-ExecutionPolicy -Scope Process RemoteSigned
```

Linux / macOS (Bash)
```
cd "vision space exam/step1"
chmod +x scripts/dev.sh
# 동시에 실행 / 개별 실행
./scripts/dev.sh --all
./scripts/dev.sh --backend
./scripts/dev.sh --frontend
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

CHROMA_PERSIST_DIR=../../chroma   # apps/api 기준 상대경로(운영은 절대경로 권장)
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
ALLOW_ORIGINS=http://localhost:3000
PROMPT_FILE=rag/prompts/answer.txt   # 선택: 프롬프트 파일 경로(PROMPT_PATH도 지원)
```

프론트엔드(`step1/apps/web/.env.local`)
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## 백엔드 API (요약)
- `GET /health` → `{ "status": "ok" }`
- `POST /rag` (multipart/form-data) → `{ "indexed": number }`
- `POST /agent` (application/json) → `{ "answer": string, "sources": [{ "title", "page"?, "score"? }] }`
- `DELETE /docs` (application/json) → `{ "deleted": number }`

## 테스트 실행
백엔드(pytest)
```
cd "vision space exam/step1/apps/api"
python -m pytest -q
# 커버리지:
pytest --cov=app --cov-report=term-missing
```

프론트엔드(Vitest)
```
cd "vision space exam/step1/apps/web"
npm run test          # watch
npm run test:run      # 1회 실행
npm run test:coverage # 커버리지
```

## 코드 스타일
- Web(Prettier/ESLint)
  - 포맷: `npm run format`
  - 린트: `npm run lint` / `npm run lint:fix`
- API(Black/Isort/Ruff)
  - venv 활성화 후 설치: `pip install -r requirements-dev.txt`
  - 포맷/정렬/린트: `isort . && black . && ruff check . --fix`

## 참고
- 프롬프트: `.env.api`의 `PROMPT_FILE|PROMPT_PATH`로 파일 기반 프롬프트를 지정할 수 있습니다(미지정/실패 시 내장 정책으로 폴백).
- 인덱스 경로: `CHROMA_PERSIST_DIR` 상대경로는 `apps/api` 기준으로 해석됩니다.
