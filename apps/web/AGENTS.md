# AGENTS.md (Web)

요약: FastAPI RAG 백엔드를 사용하는 Next.js(앱 라우터) 웹 프런트엔드입니다. 질의 엔드포인트는 `/agent`로 일원화되어 답변과 출처(sources)를 함께 표시합니다.

## 범위
- 위치: `step1/apps/web`
- 역할: 문서 업로드/삭제 및 질의(답변 + 출처) UI
- 스택: Next.js(App Router, TypeScript), Axios

## 주요 파일
- `app/page.tsx`: 질의 페이지
- `app/rag/page.tsx`: 업로드/삭제 페이지
- `lib/api.ts`: Axios 래퍼(askQuestion, ingestFiles, deleteDocs)

## 환경 변수
- `.env.local`: `NEXT_PUBLIC_API_BASE` (기본 `http://localhost:8000`)

## 실행/테스트
- 설치: `npm install`
- 개발: `npm run dev` → http://localhost:3000
- 빌드: `npm run build`
- 실행: `npm start -p 3000`
- 테스트: `npm run test`(watch), `npm run test:run`, `npm run test:coverage`

## API 계약(프런트 기준)
- `GET /health` → `{ "status": "ok" }`
- `POST /rag` (multipart/form-data)
  - 바디: `files` (다중 업로드)
  - 응답: `{ "indexed": number }`
- `DELETE /docs` (application/json)
  - 바디: `{ "title": string, "page"?: number }`
  - 응답: `{ "deleted": number }`
- `POST /agent` (application/json)
  - 바디: `{ "question": string, "top_k"?: number }`
  - 응답: `{ "answer": string, "sources": [{ "title": string, "page"?: number, "score"?: number }] }`

## UI 동작
- RAG(/rag): 파일 업로드 시 `indexed: N` 표시, title(+page)로 삭제 시 `deleted: N` 표시
- Agent(/agent): 질문/`top_k` 입력 후 답변과 출처 목록 표시

## Code Style (Web)
- 포맷터: Prettier(`.prettierrc.json`); 실행 `npm run format`
- 린터: ESLint(`next lint`), 핵심 규칙 `no-duplicate-imports`
- 실행: `npm run lint`, `npm run lint:fix`

## Refactoring Guidelines (Web)
- 페이지 구조: 기본 질의는 `/agent`, 업로드/삭제는 `/rag`. 페이지는 `app/` 하위에서 역할 분리 유지.
- 컴포넌트 분리: 공용 UI는 `components/`로 이동(예: LoadingButton, Notice). 페이지는 최소 로직만.
- 임포트 규칙: `import React, { useX } from 'react';` 형태로 일관. 중복 임포트 금지(ESLint `no-duplicate-imports`).
- API 경계: 네트워크 호출은 `lib/api.ts`에서만(askQuestion, ingestFiles, deleteDocs, toErrorMessage).
- 상태 관리: 단순 state는 `useState`. 복잡해지면 분리/리팩토링 고려(전역 상태는 필요 시).
- 접근성: `label` 연결, 알림은 `Notice`에 위임(`role="alert|status"`), 인터랙션은 `<button>` 사용.
- 스타일: 전역 스타일은 `app/globals.css`에서 관리. 일관된 타이포그래피/여백 유지.
- 테스트: RTL+Vitest로 컴포넌트/페이지 테스트, axios는 모킹으로 네트워크 차단. 테스트는 독립적으로 유지.
- 인코딩: 모든 파일은 UTF-8 유지.

