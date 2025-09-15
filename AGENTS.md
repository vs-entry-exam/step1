# AGENTS.md (Project)

목적: Step1 전체 프로젝트의 목표, 구조, 실행/테스트 방법을 한 곳에 요약하고, 세부 내용은 각 범위별 문서로 연결합니다.

참조 문서
- Web: `vision space exam/step1/apps/web/AGENTS.md`
- API: `vision space exam/step1/apps/api/AGENTS.md`

---

## 개요
- 목표: 문서 기반 RAG QA MVP(업로드→인덱싱→검색→응답, 출처 포함)
- 스택: Next.js(App Router) · FastAPI · LangChain · ChromaDB · OpenAI/Ollama
- 라벨: Ask ↔ RAG(헤더 토글), Upload(/ingest)

## 아키텍처
- 프론트엔드: `/ingest` 업로드/삭제 UI, `/` 질문 UI
- 백엔드: `/ingest` 파일 수신→파이프라인→Chroma upsert, `/ask` 검색→LLM 답변, `DELETE /docs` 삭제
- 저장소: ChromaDB 로컬 퍼시스트(`step1/chroma`)
- 프롬프트: 파일 기반 로딩(캐시) + 폴백 정책

## 폴더 구조(요약)
```
step1/
├─ apps/
│  ├─ web/         # 프론트엔드(Ask/Upload)
│  └─ api/         # 백엔드(app 패키지)
├─ chroma/
├─ data/
├─ .env.api
└─ README.md
```

## 실행(로컬)
- 백엔드: `cd step1/apps/api && uvicorn app.main:app --reload`
- 프론트: `cd step1/apps/web && npm run dev`
- 스크립트(동시 실행)
  - Windows: `powershell -File step1/scripts/dev.ps1 -All`
  - Linux/macOS: `step1/scripts/dev.sh --all`

## 환경/프롬프트
- `.env.api`의 `PROMPT_FILE|PROMPT_PATH`로 프롬프트 경로 지정(기본 파일, 실패 시 폴백)
- `CHROMA_PERSIST_DIR` 상대경로는 `apps/api` 기준

## API 요약
- `GET /health`, `POST /ingest`, `POST /ask`, `DELETE /docs`
- 상세 계약/구현: `apps/api/AGENTS.md`

## 테스트 개요
- 백엔드(pytest): venv 활성화 후 `python -m pytest -q`
- 프론트(Vitest): `cd step1/apps/web && npm run test:run`

