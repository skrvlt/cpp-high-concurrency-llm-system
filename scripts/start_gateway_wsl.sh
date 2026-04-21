#!/usr/bin/env bash
set -euo pipefail

GATEWAY_PORT="${GATEWAY_PORT:-8080}"
UPSTREAM_HOST="${UPSTREAM_HOST:-127.0.0.1}"
UPSTREAM_PORT="${UPSTREAM_PORT:-8000}"

cd cpp_gateway
mkdir -p build
cd build

if [[ ! -x "./llm_gateway" ]]; then
  cmake ..
  make
fi

echo "Starting gateway on port ${GATEWAY_PORT}, upstream=${UPSTREAM_HOST}:${UPSTREAM_PORT}"
GATEWAY_PORT="${GATEWAY_PORT}" \
UPSTREAM_HOST="${UPSTREAM_HOST}" \
UPSTREAM_PORT="${UPSTREAM_PORT}" \
./llm_gateway
