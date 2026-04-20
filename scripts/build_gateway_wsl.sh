#!/usr/bin/env bash
set -euo pipefail

cd cpp_gateway
mkdir -p build
cd build
cmake ..
make
echo "Gateway build completed. Run ./llm_gateway to start the epoll gateway on port 8080."
