#!/usr/bin/env bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_PID=
FRONTEND_PID=

cleanup() {
  echo "Shutting down..."
  [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
  [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
  exit 0
}
trap cleanup INT TERM

echo "Starting backend (LangGraph)..."
(cd "$ROOT/sql-agent" && ( [ -f venv/bin/activate ] && . venv/bin/activate; langgraph dev --no-browser )) &
BACKEND_PID=$!

sleep 2

echo "Starting frontend (Next.js)..."
(cd "$ROOT/agent-chat-ui" && pnpm dev) &
FRONTEND_PID=$!

wait
