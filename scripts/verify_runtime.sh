#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-direct}"
HOST_ADDRESS="${2:-127.0.0.1}"
API_PORT="${3:-8000}"
GATEWAY_PORT="${4:-8080}"

if [[ "${MODE}" == "gateway" ]]; then
  PORT="${GATEWAY_PORT}"
else
  PORT="${API_PORT}"
fi

BASE_URI="http://${HOST_ADDRESS}:${PORT}/api"

echo "Verify mode: ${MODE}"
echo "Base URI: ${BASE_URI}"

echo "Health response:"
curl -s "${BASE_URI}/health"

echo
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URI}/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}')

echo "Login response:"
echo "${LOGIN_RESPONSE}"

TOKEN=$(printf '%s' "${LOGIN_RESPONSE}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')

echo "Chat response:"
curl -s -X POST "${BASE_URI}/chat" \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"${TOKEN}\",\"message\":\"请返回当前运行模式的验证信息\"}"
