#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATEWAY_PORT="${GATEWAY_PORT:-18080}"
UPSTREAM_PORT="${UPSTREAM_PORT:-8000}"
API_MODE="${API_MODE:-local}"
UPSTREAM_HOST="${UPSTREAM_HOST:-127.0.0.1}"

cleanup() {
  if [[ -n "${API_PID:-}" ]] && kill -0 "${API_PID}" >/dev/null 2>&1; then
    kill "${API_PID}" >/dev/null 2>&1 || true
    wait "${API_PID}" 2>/dev/null || true
  fi
  if [[ -n "${GATEWAY_PID:-}" ]] && kill -0 "${GATEWAY_PID}" >/dev/null 2>&1; then
    kill "${GATEWAY_PID}" >/dev/null 2>&1 || true
    wait "${GATEWAY_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT

cd "${ROOT_DIR}"
bash scripts/build_gateway_wsl.sh

if [[ "${API_MODE}" == "local" ]]; then
  VENV_PYTHON="${ROOT_DIR}/.venv-wsl/bin/python"
  if [[ ! -x "${VENV_PYTHON}" ]]; then
    echo "Missing WSL virtual environment. Run: bash scripts/setup_wsl_python.sh" >&2
    exit 1
  fi
  echo "Starting local WSL API on 127.0.0.1:${UPSTREAM_PORT}"
  PYTHONPATH="${ROOT_DIR}" \
  "${VENV_PYTHON}" -m uvicorn services.ai_service.app.main:app --host 127.0.0.1 --port "${UPSTREAM_PORT}" &
  API_PID=$!
  API_READY=0
  for _ in $(seq 1 40); do
    if curl -fsS "http://127.0.0.1:${UPSTREAM_PORT}/api/health" >/dev/null 2>&1; then
      API_READY=1
      break
    fi
    sleep 0.5
  done
  if [[ "${API_READY}" -ne 1 ]]; then
    echo "Local WSL API failed to become ready on 127.0.0.1:${UPSTREAM_PORT}" >&2
    exit 1
  fi
  echo "Direct API health:"
  curl -sS "http://127.0.0.1:${UPSTREAM_PORT}/api/health"
  echo
  UPSTREAM_HOST="127.0.0.1"
fi

echo "Starting gateway validation process on ${GATEWAY_PORT}, upstream=${UPSTREAM_HOST}:${UPSTREAM_PORT}"
cd cpp_gateway/build
GATEWAY_PORT="${GATEWAY_PORT}" \
UPSTREAM_HOST="${UPSTREAM_HOST}" \
UPSTREAM_PORT="${UPSTREAM_PORT}" \
./llm_gateway &
GATEWAY_PID=$!

echo "Gateway health:"
GATEWAY_HEALTH="$(curl -sS "http://127.0.0.1:${GATEWAY_PORT}/api/health" || true)"
echo "${GATEWAY_HEALTH}"
if [[ "${GATEWAY_HEALTH}" != *'"status"'* ]]; then
  echo "Gateway health check did not return the expected success payload." >&2
  exit 1
fi
echo
cd "${ROOT_DIR}"
bash scripts/verify_runtime.sh gateway 127.0.0.1 8000 "${GATEWAY_PORT}"
echo
bash scripts/verify_gateway_smoke.sh 127.0.0.1 "${GATEWAY_PORT}"
