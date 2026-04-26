# 网关验证说明

该文档用于指导 Linux / WSL 环境下的 C++ epoll 网关验证。

## 前置检查

- 参考根目录 `.env.example` 确认 Python 服务端口和网关端口约定
- 先直接访问 `http://127.0.0.1:8000/api/health`，确认 Python 服务状态正常
- 如需改变默认转发地址，可设置 `GATEWAY_PORT`、`UPSTREAM_HOST`、`UPSTREAM_PORT`
- 如果当前 WSL 环境未安装 `cmake`，可使用脚本中的 `g++` 回退编译能力

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

该脚本会优先使用 `cmake`，若环境中不存在 `cmake`，则自动回退到 `g++` 直接编译。

若需要在同一个 WSL shell 生命周期中完成完整验证，避免一次性 `wsl.exe` 会话的后台进程管理差异，推荐执行：

```bash
API_MODE=local bash scripts/validate_gateway_wsl.sh
```

该脚本会在当前 WSL 会话中构建并启动网关，依次验证 `/api/health`、登录、问答和历史记录，然后自动回收网关进程。

参数说明：

- `API_MODE=local`：在 WSL 内部启动 Python API，适合当前机器的稳定联调
- `API_MODE=remote`：使用外部已启动 API，适合已确认 WSL 可访问目标上游的环境

若 WSL 中尚未安装 Python 依赖，可先执行：

```bash
bash scripts/setup_wsl_python.sh
```

该脚本会创建 `.venv-wsl` 虚拟环境并安装依赖，适用于 Ubuntu 默认启用 `externally-managed-environment` 限制的场景。

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

## 结果要求

- `/api/health` 能通过网关返回服务状态
- 网关可成功转发 `/api/chat`
- `/api/history` 返回会话标题和消息列表
- 当 Python 服务关闭时，网关返回 `502 Bad Gateway` 风格错误响应
