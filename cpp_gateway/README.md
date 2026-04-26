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

如果当前 WSL / Linux 环境没有安装 `cmake`，也可以直接使用 `g++` 回退编译：

```bash
g++ -std=c++17 ../src/main.cpp ../src/http_server.cpp -I../include -pthread -o llm_gateway
```

仓库内的 `scripts/build_gateway_wsl.sh` 与 `scripts/start_gateway_wsl.sh` 已经内置这条回退逻辑。

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

如果需要在单个 WSL 会话中自动完成“构建 -> 启动 -> 验证 -> 清理”，可执行：

```bash
bash scripts/validate_gateway_wsl.sh
```

该脚本支持：

- `API_MODE=local`：在 WSL 内部启动 Python API，再验证网关
- `API_MODE=remote`：使用外部已启动的 Python API，并结合 `UPSTREAM_HOST` / `UPSTREAM_PORT` 转发

如果 WSL 中尚未安装 Python 依赖，可先执行：

```bash
bash scripts/setup_wsl_python.sh
```

该脚本会在项目根目录创建 `.venv-wsl` 虚拟环境，并在其中安装所需依赖。

## 说明

当前版本重点是把网关做成可迁移、可验证的 Linux / WSL 专项模块，后续可以继续增强：

- 更完整的 HTTP 解析
- keep-alive
- 更稳定的错误处理
- 压测优化
- 更完整的请求头透传
