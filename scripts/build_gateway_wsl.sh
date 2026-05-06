#!/usr/bin/env bash
set -euo pipefail

cd cpp_gateway
mkdir -p build
cd build

if command -v cmake >/dev/null 2>&1; then
  cmake ..
  make
else
  echo "cmake not found; using direct g++ fallback build."
  g++ -std=c++17 -O2 -pthread -I../include ../src/main.cpp ../src/http_server.cpp -o llm_gateway
fi

echo "Gateway build completed. Use scripts/start_gateway_wsl.sh or run cpp_gateway/build/llm_gateway with GATEWAY_PORT / UPSTREAM_HOST / UPSTREAM_PORT."
