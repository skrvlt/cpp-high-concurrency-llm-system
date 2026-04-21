#!/usr/bin/env bash
set -euo pipefail

LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}')

echo "Login response:"
echo "${LOGIN_RESPONSE}"

TOKEN=$(printf '%s' "${LOGIN_RESPONSE}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')

echo "Chat response:"
curl -s -X POST http://127.0.0.1:8080/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"token\":\"${TOKEN}\",\"message\":\"请通过网关回答当前系统目标\"}"

echo
echo "History response:"
curl -s "http://127.0.0.1:8080/api/history?token=${TOKEN}"
