# AGENTS.md (Web)

목적: FastAPI RAG 백엔드와 통신하는 Next.js 프론트엔드의 현재 상태와 사용 방법을 정리합니다.

## 범위
- 디렉터리: `step1/apps/web`
- 역할: 문서 업로드(인덱싱)와 질의(출처 포함 답변)용 최소 UI
- 스택: Next.js(App Router, TypeScript), Axios

## MVP 기능
- `/rag`: 문서 업로드/삭제(Chroma 인덱스 관리)
- `/agent`: 질문 입력 → 한국어 답변(Agent; Retrieval Tool 사용)
- 헤더 토글: Ask ↔ RAG 전환

## 디렉터리 구조(주요)
- `app/page.tsx`: Ask 페이지
- `app/rag/page.tsx`: Upload/삭제 페이지
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

- `GET /health` → `{ "status": "ok" }`
- `POST /rag` (multipart/form-data)
  - 필드: `files` (다중 허용)
  - 응답: `{ "indexed": number }`
- `POST /ask` (application/json)
  - 요청: `{ "question": string, "top_k"?: number }`
  - 응답: `{ "answer": string, "sources": [{ "title": string, "page"?: number, "score"?: number }] }`
- `DELETE /docs` (application/json)
  - 요청: `{ "title": string, "page"?: number }`
  - 응답: `{ "deleted": number }`
- `POST /agent` (application/json)
  - 요청: `{ "question": string, "top_k"?: number }`
  - 응답: `{ "answer": string, "sources": [] }`

## UI 동작
- RAG(/rag): 파일 다중 선택 업로드 → `indexed: N` 표시, title(+page)로 삭제 → `deleted: N`
- Agent(/agent): 질문/`top_k` 입력 → `/agent` 호출 → 답변 표시(필요 시 RAG Retrieval Tool 사용)
- 접근성: `Notice`는 kind에 따라 `role="alert|status"` 제공

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
- `tests/rag.page.test.tsx`: Upload 페이지 삭제 유효성

## Code Style (Web)
- 포맷터: Prettier (`.prettierrc.json`)
- 린터: ESLint (`next lint`), `no-duplicate-imports` 활성화
- 실행: `npm run lint` / `npm run lint:fix` / `npm run format`

## Scripts
- 동시 실행(개발):
  - Windows: `powershell -File step1/scripts/dev.ps1 -All`
  - Linux/macOS: `step1/scripts/dev.sh --all`

---

## Refactoring Guidelines (Web)
- 라우팅/페이지: 기본 `/agent`, 업로드/삭제는 `/rag`에 유지. 페이지는 `app/` 하위에 배치하고 역할을 혼합하지 않는다.
- 컴포넌트화: 반복되는 UI는 `components/`로 분리(예: LoadingButton, Notice). 페이지 내 중복 로직은 함수/훅으로 추출 고려.
- 임포트 규칙: `import React, { useX } from 'react';` 한 줄 사용. 동일 모듈 중복 임포트 금지(ESLint `no-duplicate-imports`).
- API 계층: 네트워크 호출은 `lib/api.ts`에만 구현(askQuestion, ingestFiles, deleteDocs, toErrorMessage 등 헬퍼 사용).
- 상태관리: 단순 상태는 `useState`. 복잡하면 커스텀 훅으로 분리. 전역 상태 도입은 필요 시 검토.
- 접근성: 폼 요소에 `label` 연결, 알림은 `Notice`로 렌더(kind별 `role=alert|status`). 버튼은 의미에 맞게 `<button>` 사용.
- 스타일: 전역 토큰(`globals.css`) 우선 사용. 패널/레이아웃 클래스 재사용, 과도한 인라인 스타일 지양.
- 테스트: 새 페이지/컴포넌트는 RTL+Vitest로 테스트. axios는 모킹, 텍스트 일치보다는 역할/상태 기반 매칭 권장.
- 국제화/문자셋: 기본 한글 UI. 테스트는 한글 문자열 의존 최소화(정규식/역할 사용). 모든 파일은 UTF‑8 저장.
