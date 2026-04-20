#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-5500}"

python3 -m http.server "${PORT}"
