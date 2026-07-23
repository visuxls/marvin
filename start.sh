#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

API_HOST="127.0.0.1"
API_PORT="7932"
UI_URL="http://localhost:3000"
VERSION="$(sed -n 's/^version = "\([^"]*\)"/\1/p' pyproject.toml | head -1)"
VERSION="${VERSION:-0.1.0}"

lan_ip() {
  if command -v ipconfig >/dev/null 2>&1; then
    ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true
  fi
}

LAN_IP="$(lan_ip)"
LAN_UI_URL=""
if [[ -n "${LAN_IP}" ]]; then
  LAN_UI_URL="http://${LAN_IP}:3000"
fi

trap 'kill 0' EXIT INT TERM

print_banner() {
  local bold="" dim="" cyan="" reset=""
  if [[ -t 1 && -z "${NO_COLOR:-}" ]]; then
    bold=$'\033[1m'
    dim=$'\033[2m'
    cyan=$'\033[38;5;80m'
    reset=$'\033[0m'
  fi

  printf '%s\n' \
    "" \
    "  ${bold}Marvin${reset} ${dim}v${VERSION}${reset}" \
    "  ${dim}Personal CFO assistant${reset}" \
    "" \
    "  ${cyan}●${reset} ${dim}API${reset}  ${bold}http://${API_HOST}:${API_PORT}${reset}" \
    "  ${cyan}●${reset} ${dim}UI${reset}   ${bold}${UI_URL}${reset}  ${dim}· opens when ready${reset}"

  if [[ -n "${LAN_UI_URL}" ]]; then
    printf '%s\n' \
      "  ${cyan}●${reset} ${dim}LAN${reset}  ${bold}${LAN_UI_URL}${reset}  ${dim}· phone / other devices${reset}"
  fi

  printf '%s\n' \
    "" \
    "  ${dim}Press Ctrl+C to stop both${reset}" \
    ""
}

print_banner

uv run uvicorn app:app \
  --host "${API_HOST}" \
  --port "${API_PORT}" \
  --log-level warning \
  --no-access-log \
  >/dev/null &

(cd frontend && MARVIN_QUIET=1 npm run --silent dev)
