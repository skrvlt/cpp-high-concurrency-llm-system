#!/usr/bin/env bash
set -euo pipefail

cd cpp_gateway
mkdir -p build
cd build
cmake ..
make
echo "Gateway build completed. Use ../scripts/start_gateway_wsl.sh or run ./llm_gateway with GATEWAY_PORT / UPSTREAM_HOST / UPSTREAM_PORT."
