# AGENTS.md (Web)

목적: FastAPI RAG 백엔드와 통신하는 Next.js 프론트엔드의 현재 상태와 사용 방법을 정리합니다.

## 범위
- 디렉터리: `step1/apps/web`
- 역할: 문서 업로드(인덱싱)와 질의(출처 포함 답변)용 최소 UI
- 스택: Next.js(App Router, TypeScript), Axios

## MVP 기능
- `/ingest`(Upload): PDF/MD/TXT 다중 파일 업로드 → `indexed: N` 표시
- `/`(Ask): 질문 입력 → 한국어 답변과 출처 리스트(`[title:page]`) 표시
- 헤더 토글: Ask ↔ RAG 전환

## 디렉터리 구조(주요)
- `app/page.tsx`: Ask 페이지
- `app/ingest/page.tsx`: Upload/삭제 페이지
- `app/layout.tsx`, `app/globals.css`: 레이아웃/전역 스타일
- `components/ModeToggle.tsx`: Ask/RAG 토글 컴포넌트
- `components/LoadingButton.tsx`, `components/Notice.tsx`: 공통 UI 컴포넌트
- `lib/api.ts`: Axios 인스턴스 및 타입/헬퍼

## 환경 변수
- 파일: `.env.local` (로컬 개발에서 자동 로드)
- 키: `NEXT_PUBLIC_API_BASE` (기본값: `http://localhost:8000`)
- 변경 시 개발 서버 재시작 필요

## 스크립트
- 설치: `npm install`
- 개발: `npm run dev` → http://localhost:3000
- 빌드: `npm run build`
- 실행: `npm start -p 3000`

## 백엔드 계약(현 구현 가정)
- `GET /health` → `{ "status": "ok" }`
- `POST /ingest` (multipart/form-data)
  - 필드: `files` (다중 허용)
  - 응답: `{ "indexed": number }`
- `POST /ask` (application/json)
  - 요청: `{ "question": string, "top_k"?: number }`
  - 응답: `{ "answer": string, "sources": [{ "title": string, "page"?: number, "score"?: number }] }`
- `DELETE /docs` (application/json)
  - 요청: `{ "title": string, "page"?: number }`
  - 응답: `{ "deleted": number }`

## UI 동작
- Upload: 파일 다중 선택 → `/ingest` 업로드 → `indexed: N` 표시, 에러/로딩 상태 표시
- Delete: title(필수) + page(선택) 입력 → `/docs` 호출 → `deleted: N` 표시
- Ask: 질문/`top_k` 입력 → `/ask` 호출 → 답변/출처 리스트 표시, 로딩/에러 처리
- 접근성: `Notice`는 kind에 따라 `role="alert|status"`를 제공

## Tests (Web)
- 도구: Vitest + React Testing Library(jsdom), jest-dom 매처
- 위치: `apps/web/tests`
- 실행:
  - `npm run test` (watch)
  - `npm run test:run` (1회)
  - `npm run test:coverage` (커버리지)
- 포함 테스트:
  - `tests/api.test.ts`: API 헬퍼(axios 모킹)
  - `tests/components.test.tsx`: LoadingButton/Notice
  - `tests/home.page.test.tsx`: Ask 페이지 상호작용
  - `tests/ingest.page.test.tsx`: Upload 페이지 삭제 유효성

## Code Style (Web)
- 포맷터: Prettier (`.prettierrc.json`)
- 린터: ESLint (`next lint`), `no-duplicate-imports` 활성화
- 실행: `npm run lint` / `npm run lint:fix` / `npm run format`

## Scripts
- 동시 실행(개발):
  - Windows: `powershell -File step1/scripts/dev.ps1 -All`
  - Linux/macOS: `step1/scripts/dev.sh --all`
