# 网关验证说明

该文档用于指导 Linux / WSL 环境下的 C++ epoll 网关验证。

## 前置检查

- 参考根目录 `.env.example` 确认 Python 服务端口和网关端口约定
- 先直接访问 `http://127.0.0.1:8000/api/health`，确认 Python 服务状态正常
- 如需改变默认转发地址，可设置 `GATEWAY_PORT`、`UPSTREAM_HOST`、`UPSTREAM_PORT`

## 目标

验证以下内容：

1. `cpp_gateway` 在 WSL 或 Linux 下可编译
2. 网关启动后监听 `8080`
3. Python 服务启动后，网关可将请求转发到 `8000`
4. `/api/login`、`/api/chat`、`/api/history` 主链路通过网关可用
5. 上游服务未启动时，网关返回明确错误

## WSL 实测记录

当前分支已在 WSL 环境完成一次完整联调验证。验证时 Windows 侧启动 Python FastAPI 服务，WSL 侧编译并启动 C++ 网关，网关端口临时设置为 `18081` 以避免占用默认演示端口。WSL 中未安装 `cmake` 时，`scripts/build_gateway_wsl.sh` 自动回退到 `g++ -std=c++17` 直编方式并生成 `cpp_gateway/build/llm_gateway`。

实测命令如下：

```bash
bash scripts/build_gateway_wsl.sh
GATEWAY_PORT=18081 UPSTREAM_HOST=127.0.0.1 UPSTREAM_PORT=8000 bash scripts/start_gateway_wsl.sh
bash scripts/verify_runtime.sh gateway 127.0.0.1 8000 18081
bash scripts/verify_gateway_smoke.sh 127.0.0.1 18081
```

实测结果表明，网关能够通过 `127.0.0.1:8000` 访问 Python 服务，并经由网关完成 `/api/health`、`/api/login`、`/api/chat` 与 `/api/history` 验证。启动日志示例如下：

```text
Starting gateway on port 18081, upstream=127.0.0.1:8000
LLM gateway listening on 0.0.0.0:18081, upstream=127.0.0.1:8000
```

为避免 WSL 环境中的代理变量干扰本机端口验证，Linux Shell 验证脚本统一使用 `curl --noproxy "*"` 访问本地服务。

## 网关实现审查记录

当前 `cpp_gateway` 的核心实现位于 `cpp_gateway/src/http_server.cpp`、`cpp_gateway/include/http_server.h`、`cpp_gateway/src/main.cpp` 和 `cpp_gateway/include/thread_pool.h`。代码审查结论如下：

| 项目 | 当前实现 |
| --- | --- |
| listener port | 默认监听 `8080`，由 `GATEWAY_PORT` 覆盖 |
| upstream host | 默认 `127.0.0.1`，由 `UPSTREAM_HOST` 覆盖 |
| upstream port | 默认 `8000`，由 `UPSTREAM_PORT` 覆盖 |
| epoll usage | 主循环调用 `epoll_wait` 监听连接和读事件 |
| thread pool usage | 读事件从 epoll 循环移除后交给 `ThreadPool` 执行 `HandleClient` |
| request forwarding | `ForwardToUpstream` 将 GET/POST 请求转发给 Python FastAPI 服务 |
| upstream failure behavior | 上游 socket 创建、地址转换、连接和响应为空时统一返回 `502 Bad Gateway` |
| documented validation command | `bash scripts/verify_runtime.sh gateway` 与 `bash scripts/verify_gateway_smoke.sh` |

网关错误响应由 `BuildErrorResponse` 生成，HTTP 状态行为为 `502 Bad Gateway`，响应体采用 JSON 格式，例如：

```json
{"error":"failed to connect upstream"}
```

## 启动顺序

1. 启动 Python 服务
2. 启动前端静态服务
3. 编译并启动 C++ 网关
4. 执行 `bash scripts/verify_runtime.sh gateway`
5. 使用浏览器的 `?mode=gateway` 或 curl 执行补充验证

推荐直接执行：

```bash
bash scripts/start_gateway_wsl.sh
```

## 关键验证命令

### 登录

```bash
curl -X POST http://127.0.0.1:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}'
```

### 问答

```bash
curl -X POST http://127.0.0.1:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"token":"<token>","message":"通过网关提问"}'
```

### 历史记录

```bash
curl "http://127.0.0.1:8080/api/history?token=<token>"
```

### 上游失败验证

为了验证 Python 服务不可用时的网关错误处理，可以临时把上游端口指向一个未监听端口，例如 `65530`：

```bash
GATEWAY_PORT=8080 UPSTREAM_HOST=127.0.0.1 UPSTREAM_PORT=65530 bash scripts/start_gateway_wsl.sh
```

然后在另一个终端访问：

```bash
curl -i http://127.0.0.1:8080/api/health
```

预期结果包含：

```text
HTTP/1.1 502 Bad Gateway
{"error":"failed to connect upstream"}
```

### 网关压测

项目提供 `scripts/benchmark_gateway.py` 用于在 Linux / WSL 下生成可复现的并发测试结果。健康检查链路适合验证 C++ 网关接入吞吐能力：

```bash
python scripts/benchmark_gateway.py \
  --base-url http://127.0.0.1:8080 \
  --scenario health \
  --requests 1000 \
  --concurrency 100 \
  --output output/benchmark/gateway-health.json
```

智能问答链路适合验证网关转发与 Python 服务协同能力：

```bash
python scripts/benchmark_gateway.py \
  --base-url http://127.0.0.1:8080 \
  --scenario chat \
  --requests 300 \
  --concurrency 30 \
  --output output/benchmark/gateway-chat.json
```

结果文件包含平均响应时间、P95 响应时间、`throughput_rps`、成功率、错误率和错误样例，可直接作为论文第 6 章实验表格的原始数据来源。

### M6 压测实测结果

本次 M6 压测在 Windows + WSL 联调环境完成。Python 服务运行在 `127.0.0.1:8000`，C++ 网关运行在 WSL 中，因本机 `8080` 端口被其他服务占用，实测网关端口使用 `18081`。压测命令如下：

```bash
python scripts/benchmark_gateway.py \
  --base-url http://127.0.0.1:18081 \
  --scenario health \
  --requests 1000 \
  --concurrency 100 \
  --output output/benchmark/gateway-health.json

python scripts/benchmark_gateway.py \
  --base-url http://127.0.0.1:18081 \
  --scenario chat \
  --requests 300 \
  --concurrency 30 \
  --output output/benchmark/gateway-chat.json
```

实测结果如下：

| 场景 | 总请求数 | 并发数 | 平均响应时间/ms | P95 响应时间/ms | throughput_rps | 成功率/% | 错误数 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| health | 1000 | 100 | 134.21 | 166.90 | 635.41 | 100.00 | 0 |
| chat | 300 | 30 | 43.67 | 65.21 | 642.10 | 100.00 | 0 |

压测过程中曾发现并发 POST 请求体读取不完整会导致少量 422 错误。当前网关已根据 `Content-Length` 读取完整请求体后再转发，修复后 health 与 chat 两类场景均达到 100% 成功率。

## 结果要求

- `/api/health` 能通过网关返回服务状态
- 网关可成功转发 `/api/chat`
- `/api/history` 返回会话标题和消息列表
- 当 Python 服务关闭时，网关返回 `502 Bad Gateway` 风格错误响应
- `scripts/benchmark_gateway.py` 可生成包含 P95 和 `throughput_rps` 的 JSON 压测结果
