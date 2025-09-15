#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
ROOT_DIR="$(cd -- "${SCRIPT_DIR}/.." &>/dev/null && pwd)"

usage() {
  cat <<EOF
Usage: ${0##*/} [--backend | --frontend | --all]

Options:
  --backend   Start FastAPI backend (uvicorn)
  --frontend  Start Next.js frontend (npm run dev)
  --all       Start both backend and frontend in parallel

Notes:
  - Uses .venv if present (no need to source); falls back to system python.
  - Runs from project root automatically.
EOF
}

start_backend() {
  cd "${ROOT_DIR}/apps/api"
  echo "[dev.sh] Starting backend (FastAPI)..."
  if [[ -x .venv/bin/python ]]; then
    PY=".venv/bin/python"
  else
    PY="python"
  fi
  exec_cmd=("${PY}" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload)
  "${exec_cmd[@]}"
}

start_frontend() {
  cd "${ROOT_DIR}/apps/web"
  echo "[dev.sh] Starting frontend (Next.js)..."
  npm run dev
}

case "${1:-}" in
  --backend)
    start_backend
    ;;
  --frontend)
    start_frontend
    ;;
  --all)
    # Run both in background and wait
    set +e
    ( start_backend ) & PID_BACK=$!
    ( start_frontend ) & PID_FRONT=$!
    trap 'kill ${PID_BACK} ${PID_FRONT} 2>/dev/null || true' INT TERM EXIT
    wait ${PID_BACK} ${PID_FRONT}
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage
    exit 1
    ;;
esac
