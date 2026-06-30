#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

trap 'kill 0' EXIT INT TERM

echo "Marvin API:  http://127.0.0.1:7932"
echo "Marvin UI:   http://localhost:3000 (opens in your browser when ready)"
echo "Press Ctrl+C to stop both."
echo

uv run uvicorn app:app --host 127.0.0.1 --port 7932 &
(cd frontend && npm run dev)
