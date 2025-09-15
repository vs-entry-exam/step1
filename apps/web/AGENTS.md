# AGENTS.md (Web)

목적: FastAPI RAG 백엔드와 통신하는 Next.js 프론트엔드의 현재 상태와 사용 방법을 정리합니다.

## 범위
- 디렉터리: `step1/apps/web`
- 역할: 문서 업로드(인덱싱)와 질의(출처 포함 답변)용 최소 UI
- 스택: Next.js(App Router, TypeScript), Axios

## MVP 기능
- `/ingest`: PDF/MD/TXT 다중 파일 업로드 → `indexed: N` 표시
- `/`(Ask): 질문 입력 → 한국어 답변과 출처 리스트(`[title:page]`) 표시
- 헤더 토글: Ask ↔ RAG 전환

## 디렉터리 구조(주요)
- `app/page.tsx`: Ask 페이지
- `app/ingest/page.tsx`: Upload 페이지
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
  - 답변은 한국어이며 출처는 `[title:page]` 규칙을 따른다
- `DELETE /docs` (application/json)
  - 요청: `{ "title": string, "page"?: number }`
  - 응답: `{ "deleted": number }`

## UI 동작
- Upload
  - 파일 다중 선택 → `FormData`로 `/ingest` 전송 → `indexed: N` 표시
  - 진행/에러 상태 표시, 삭제 패널에서 title(+page 옵션)로 삭제
- Ask
  - 질문/`top_k` 입력 → `/ask` 호출 → 답변/출처 리스트 표시
  - `score`가 있을 경우 소수 3자리로 표기, 로딩/에러 상태 처리
- 레이아웃/스타일
  - 전역 `box-sizing: border-box`로 입력 폭 오버플로우 방지
  - 헤더 우측 `ModeToggle`로 페이지 전환

## 보안/CORS
- API 키는 프론트에 두지 않는다(백엔드 `.env.api` 전용)
- 로컬 개발 시 백엔드 CORS: `ALLOW_ORIGINS=http://localhost:3000`

## 로컬 실행 참고
- 백엔드(별도): `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- 프론트: `npm run dev`
- 인제스트 예시: `curl -F "files=@../../data/sample.pdf" http://localhost:8000/ingest`
- 질의 예시: `curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' -d '{"question":"sample.pdf 핵심 요약","top_k":4}'`

---

## Refactoring Notes (Web)
- API 헬퍼 추가: `lib/api.ts`에 `askQuestion`, `ingestFiles`, `deleteDocs`, `toErrorMessage`를 도입해 각 페이지의 API 호출/에러 처리를 단순화했습니다.
- UI 컴포넌트화: 로딩 상태와 알림 표시를 일관화하기 위해 `components/LoadingButton`, `components/Notice`를 추가했습니다.
- 페이지 코드 정리: `/`(질의)와 `/ingest`(업로드/삭제) 페이지가 공통 헬퍼/컴포넌트를 사용하도록 리팩토링하여 중복을 제거하고 가독성을 개선했습니다.
- 용어 정비: 모드 토글 라벨을 Ask/RAG로, 업로드 섹션 타이틀을 Upload로 조정했습니다(라우트는 `/ingest` 유지).
