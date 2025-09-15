# AGENTS.md (Web)

역할
- Next.js 프론트엔드: 업로드(/ingest), 질문(/) UI 제공.

실행
- `cd step1/apps/web`
- 의존성 설치: `npm install`
- 개발 서버: `npm run dev -p 3000` → http://localhost:3000

환경(.env.local)
- `NEXT_PUBLIC_API_BASE=http://localhost:8000`

페이지
- `/ingest`: 파일 선택/업로드 → `indexed: N` 표시
- `/`: 질문/`top_k` 입력 → 한글 답변 + 출처 목록(`[title:page]`)

테스트
- Vitest + RTL: `npm run test` | `npm run test:run`

주의
- API 키는 프론트에 넣지 않습니다(백엔드에서만 보관).
