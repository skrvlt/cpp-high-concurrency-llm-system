# 运行说明

## 环境要求

- Python 3.11+
- FastAPI、uvicorn
- 浏览器
- Windows、Linux 或 WSL
- Linux/WSL 环境用于编译和运行 C++ 网关

首次运行前需要在项目根目录安装 Python 依赖：

```powershell
python -m pip install -r requirements.txt
```

Linux / WSL 下同样执行：

```bash
python -m pip install -r requirements.txt
```

## 统一端口

- Python 服务：`8000`
- C++ 网关：`8080`
- 前端静态服务：`5500`

## 环境变量模板

项目根目录提供 `.env.example`。建议先按该文件统一模型接口地址和端口参数，再启动服务。

数据存储相关参数包括：

- `APP_STORAGE`：默认 `memory`；设置为 `sqlite` 时启用本地持久化仓储
- `SQLITE_DB_PATH`：SQLite 数据库文件路径，默认 `runtime_data/app.sqlite3`

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

### 4. 启动 C++ 网关

```bash
bash scripts/start_gateway_wsl.sh
```

### 5. 通过网关验证运行链路

```bash
bash scripts/verify_runtime.sh gateway
bash scripts/verify_gateway_smoke.sh
```

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

## 持久化运行

如需在演示或测试中保留会话、日志和配置，可启用 SQLite 仓储。

### Windows PowerShell

```powershell
$env:APP_STORAGE="sqlite"
$env:SQLITE_DB_PATH="runtime_data/app.sqlite3"
.\scripts\start_api.ps1
```

### Linux / WSL

```bash
export APP_STORAGE=sqlite
export SQLITE_DB_PATH=runtime_data/app.sqlite3
bash scripts/start_api.sh
```

SQLite 文件属于本地运行数据，不纳入版本库。论文中的 MySQL 表结构仍以 `db/schema.sql` 为正式数据库设计依据。

## 健康检查约定

统一健康检查接口为 `/api/health`，返回字段包括：

- `status`
- `service`
- `runtime_mode`
- `storage_mode`
- `model_name`
- `session_count`

其中 `storage_mode` 返回 `memory` 或 `sqlite`，用于确认当前是否启用了 `APP_STORAGE=sqlite` 持久化模式。

## 支持边界

- Windows：前端与 Python 服务正式支持
- WSL：前端、Python 服务、C++ 网关联调正式支持
- Linux：完整部署与高并发验证目标环境
- 不承诺 Windows 原生运行 epoll 网关
