# AGENTS.md (Root)

목표
- 업로드한 문서를 RAG로 색인하고, 웹 UI에서 질문하면 출처를 포함해 답합니다.

스택
- Next.js(App Router) · FastAPI · LangChain · ChromaDB · OpenAI/Ollama

디렉터리
- apps/web: 프론트(UI: Ask, Ingest)
- apps/api: 백엔드(API: /health, /ingest, /ask, /docs)
- rag/prompts: 답변 프롬프트 템플릿
- chroma: ChromaDB 로컬 영속 디렉터리

로컬 실행 요약
- 백엔드: `cd step1/apps/api && uvicorn app.main:app --reload`
- 프론트: `cd step1/apps/web && npm install && npm run dev -p 3000`
- 환경 변수: 루트 `.env.api`, 웹 `.env.local` 사용(키는 백엔드에만 보관)

중요 원칙
- 프론트에 API 키를 노출하지 않습니다.
- 인덱싱과 질의에 동일한 임베딩 모델을 사용합니다.
- CORS 화이트리스트는 `.env.api`의 `ALLOW_ORIGINS`로 제한합니다.

세부 가이드
- `apps/api/AGENTS.md`: API 상세(엔드포인트, 환경 변수, 실행)
- `apps/web/AGENTS.md`: Web 상세(페이지, 실행, 테스트)

커밋 규칙(요약)
- 형식: `type(scope): subject`
- 타입: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- 예: `feat(api): /ask 엔드포인트 추가`

