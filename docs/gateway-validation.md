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

## 结果要求

- `/api/health` 能通过网关返回服务状态
- 网关可成功转发 `/api/chat`
- `/api/history` 返回会话标题和消息列表
- 当 Python 服务关闭时，网关返回 `502 Bad Gateway` 风格错误响应
- `scripts/benchmark_gateway.py` 可生成包含 P95 和 `throughput_rps` 的 JSON 压测结果
