# Linux / WSL C++ 高并发接入层

该目录提供毕业设计中的 C++ epoll 高并发网关，目标环境为 `Linux` 和 `WSL`。

## 功能

- 监听 HTTP 连接
- 使用 epoll 管理事件
- 使用线程池处理任务
- 解析基础 HTTP 报文
- 将业务请求转发到 Python FastAPI 服务

## 编译

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

## 建议验证链路

1. 在 Windows、Linux 或 WSL 中启动 Python 服务
2. 在 Linux / WSL 中编译并启动网关
3. 使用 `scripts/start_gateway_wsl.sh` 启动网关
4. 使用 `scripts/verify_runtime.sh gateway` 先验证 `/api/health`、`/api/login`、`/api/chat`
5. 使用 `scripts/verify_gateway_smoke.sh` 或 `scripts/verify_gateway_smoke.ps1` 补充验证 `/api/history`

## 说明

当前版本重点是把网关做成可迁移、可验证的 Linux / WSL 专项模块，后续可以继续增强：

- 更完整的 HTTP 解析
- keep-alive
- 更稳定的错误处理
- 压测优化
- 更完整的请求头透传
