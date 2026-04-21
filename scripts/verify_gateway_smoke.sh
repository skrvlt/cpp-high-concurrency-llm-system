#!/usr/bin/env bash
set -euo pipefail

HOST_ADDRESS="${1:-127.0.0.1}"
GATEWAY_PORT="${2:-8080}"
BASE_URI="http://${HOST_ADDRESS}:${GATEWAY_PORT}/api"

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
  -d "{\"token\":\"${TOKEN}\",\"message\":\"请通过网关回答当前系统目标\"}"

echo
echo "History response:"
curl -s "${BASE_URI}/history?token=${TOKEN}"
