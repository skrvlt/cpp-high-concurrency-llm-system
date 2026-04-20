#!/usr/bin/env bash
set -euo pipefail

HOST_ADDRESS="${1:-127.0.0.1}"
PORT="${2:-8000}"

python3 -m uvicorn services.ai_service.app.main:app --host "${HOST_ADDRESS}" --port "${PORT}"
