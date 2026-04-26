#!/usr/bin/env bash
set -euo pipefail

cd cpp_gateway
mkdir -p build
cd build

if command -v cmake >/dev/null 2>&1; then
  cmake ..
  make
  echo "Gateway build completed with cmake. Use ../scripts/start_gateway_wsl.sh or run ./llm_gateway with GATEWAY_PORT / UPSTREAM_HOST / UPSTREAM_PORT."
else
  echo "cmake not found, falling back to direct g++ build."
  g++ -std=c++17 ../src/main.cpp ../src/http_server.cpp -I../include -pthread -o llm_gateway
  echo "Gateway build completed with g++ fallback. Use ../scripts/start_gateway_wsl.sh or run ./llm_gateway with GATEWAY_PORT / UPSTREAM_HOST / UPSTREAM_PORT."
fi
