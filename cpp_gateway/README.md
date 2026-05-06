# Linux / WSL C++ 高并发接入层

该目录提供毕业设计中的 C++ epoll 高并发网关，目标环境为 `Linux` 和 `WSL`。

## 功能

- 监听 HTTP 连接
- 使用 epoll 管理事件
- 使用线程池处理任务
- 解析基础 HTTP 报文
- 将业务请求转发到 Python FastAPI 服务

## 编译

推荐在仓库根目录使用项目脚本：

```bash
bash scripts/build_gateway_wsl.sh
```

脚本会优先使用 CMake；如果环境中没有安装 `cmake`，则自动回退到 `g++ -std=c++17` 直接编译。

也可以手动使用 CMake：

```bash
mkdir -p build
cd build
cmake ..
make
```

## 运行

```bash
./llm_gateway
```

默认监听：

- 网关端口：`8080`
- 上游 Python 服务：`127.0.0.1:8000`

也可以通过环境变量覆盖：

- `GATEWAY_PORT`
- `UPSTREAM_HOST`
- `UPSTREAM_PORT`

启动时会输出实际监听端口和上游地址，例如：

```text
LLM gateway listening on 0.0.0.0:8080, upstream=127.0.0.1:8000
```

## 建议验证链路

1. 在 Windows、Linux 或 WSL 中启动 Python 服务
2. 在 Linux / WSL 中编译并启动网关
3. 使用 `scripts/start_gateway_wsl.sh` 启动网关
4. 使用 `scripts/verify_runtime.sh gateway` 先验证 `/api/health`、`/api/login`、`/api/chat`
5. 使用 `scripts/verify_gateway_smoke.sh` 或 `scripts/verify_gateway_smoke.ps1` 补充验证 `/api/history`

在 WSL 中如需避开默认端口，可使用：

```bash
GATEWAY_PORT=18081 UPSTREAM_HOST=127.0.0.1 UPSTREAM_PORT=8000 bash scripts/start_gateway_wsl.sh
bash scripts/verify_runtime.sh gateway 127.0.0.1 8000 18081
bash scripts/verify_gateway_smoke.sh 127.0.0.1 18081
```

如果需要在单个 WSL 会话中完成“构建 -> 启动 -> 验证 -> 清理”，可执行：

```bash
bash scripts/validate_gateway_wsl.sh
```

该脚本支持 `API_MODE=local` 和 `API_MODE=remote`。`API_MODE=local` 会在 WSL 内部启动 Python API 后再验证网关；`API_MODE=remote` 用于连接已经启动的外部 Python API。

实测启动日志示例：

```text
Starting gateway on port 18081, upstream=127.0.0.1:8000
LLM gateway listening on 0.0.0.0:18081, upstream=127.0.0.1:8000
```

## 上游异常行为

当 Python FastAPI 服务未启动、`UPSTREAM_HOST` 无效或 `UPSTREAM_PORT` 指向未监听端口时，网关不会直接崩溃，而是返回 `502 Bad Gateway` 风格的 JSON 错误响应。可使用以下命令验证：

```bash
GATEWAY_PORT=8080 UPSTREAM_HOST=127.0.0.1 UPSTREAM_PORT=65530 ./llm_gateway
curl -i http://127.0.0.1:8080/api/health
```

预期响应包含：

```text
HTTP/1.1 502 Bad Gateway
{"error":"failed to connect upstream"}
```

## 说明

当前版本重点是把网关做成可迁移、可验证的 Linux / WSL 专项模块，后续可以继续增强：

- 更完整的 HTTP 解析
- keep-alive
- 更稳定的错误处理
- 压测优化
- 更完整的请求头透传
