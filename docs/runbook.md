# 运行说明

## 环境要求

- Python 3.11+
- FastAPI、uvicorn
- 浏览器
- Windows、Linux 或 WSL
- Linux/WSL 环境用于编译和运行 C++ 网关

## 统一端口

- Python 服务：`8000`
- C++ 网关：`8080`
- 前端静态服务：`5500`

## 环境变量模板

项目根目录提供 `.env.example`。建议先按该文件统一模型接口地址和端口参数，再启动服务。

网关相关参数包括：

- `GATEWAY_PORT`
- `UPSTREAM_HOST`
- `UPSTREAM_PORT`

## Windows 运行

### 1. 启动 Python 服务

```powershell
.\scripts\start_api.ps1
```

服务启动后可执行：

```powershell
.\scripts\verify_runtime.ps1 -Mode direct
```

用于验证 `/api/health`、登录和问答主链路。

### 2. 启动前端静态服务

```powershell
.\scripts\start_frontend.ps1
```

### 3. 打开页面

- `http://127.0.0.1:5500/frontend/index.html`
- `http://127.0.0.1:5500/frontend/admin.html`

## Linux / WSL 运行

### 1. 启动 Python 服务

```bash
bash scripts/start_api.sh
```

服务启动后可执行：

```bash
bash scripts/verify_runtime.sh direct
```

用于验证 `/api/health`、登录和问答主链路。

### 2. 启动前端静态服务

```bash
bash scripts/start_frontend.sh
```

### 3. 编译 C++ 网关

```bash
bash scripts/build_gateway_wsl.sh
```

如果 WSL / Linux 环境中缺少 `cmake`，脚本会自动回退到 `g++` 直接编译，不需要手工改命令。

### 4. 启动 C++ 网关

```bash
bash scripts/start_gateway_wsl.sh
```

### 5. 通过网关验证运行链路

```bash
bash scripts/verify_runtime.sh gateway
bash scripts/verify_gateway_smoke.sh
```

如果希望在单个 WSL 会话里自动完成构建、启动、验证和清理，推荐直接执行：

```bash
bash scripts/validate_gateway_wsl.sh
```

默认推荐：

```bash
API_MODE=local bash scripts/validate_gateway_wsl.sh
```

这会在 WSL 内部启动 Python API，再完成网关验证，避免部分机器上 WSL 无法访问 Windows 本机服务的问题。

如果 WSL 中缺少 `fastapi`、`uvicorn`、`pydantic` 等依赖，可先执行：

```bash
bash scripts/setup_wsl_python.sh
```

该脚本会创建项目内的 `.venv-wsl` 虚拟环境，避免 Ubuntu 系统 Python 的 `PEP 668` 安装限制。

### 6. 通过网关访问前端

- `http://127.0.0.1:5500/frontend/index.html?mode=gateway`
- `http://127.0.0.1:5500/frontend/admin.html?mode=gateway`

## 真实大模型接口配置

### Windows PowerShell

```powershell
$env:LLM_API_URL="https://your-model-endpoint/v1/chat/completions"
$env:LLM_API_KEY="your-api-key"
$env:LLM_MODEL_NAME="your-model-name"
```

### Linux / WSL

```bash
export LLM_API_URL="https://your-model-endpoint/v1/chat/completions"
export LLM_API_KEY="your-api-key"
export LLM_MODEL_NAME="your-model-name"
```

未配置时，系统自动回退到演示模式，适合答辩和离线展示。

## 健康检查约定

统一健康检查接口为 `/api/health`，返回字段包括：

- `status`
- `service`
- `runtime_mode`
- `model_name`
- `session_count`

## 支持边界

- Windows：前端与 Python 服务正式支持
- WSL：前端、Python 服务、C++ 网关联调正式支持
- Linux：完整部署与高并发验证目标环境
- 不承诺 Windows 原生运行 epoll 网关
