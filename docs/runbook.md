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

模型与接口安全相关参数包括：

- `LLM_API_URL`：OpenAI-compatible chat completions 接口地址
- `LLM_API_KEY`：真实模型 API Key，不应提交到版本库
- `LLM_MODEL_NAME`：默认模型名，当前模板为 `deepseek-v4-flash`
- `LLM_PROVIDER`：当前默认 provider 名称
- `LLM_PROVIDERS_JSON`：多模型配置清单，不存放密钥
- `LLM_MODELS_JSON`：可选模型清单覆盖配置，不存放密钥
- `DEEPSEEK_API_KEY`：DeepSeek 本地密钥环境变量
- `MIMO_API_KEY`：MiMo 本地密钥环境变量
- `XIAOMI_API_KEY`：MiMo 兼容密钥环境变量
- `APP_CORS_ORIGINS`：允许访问 Python API 的前端来源列表

数据存储相关参数包括：

- `APP_STORAGE`：默认 `memory`；设置为 `sqlite` 时启用本地持久化仓储
- `SQLITE_DB_PATH`：SQLite 数据库文件路径，默认 `runtime_data/app.sqlite3`

网关相关参数包括：

- `GATEWAY_PORT`
- `UPSTREAM_HOST`
- `UPSTREAM_PORT`

## Windows 运行

## 5 分钟验收路线

1. 安装依赖：`python -m pip install -r requirements.txt`。
2. 启动 API：`.\scripts\start_api.ps1`。
3. 打开 `http://127.0.0.1:8000/api/health` 验证健康检查。
4. 启动前端：`.\scripts\start_frontend.ps1`。
5. 打开用户端页面并使用 `student / student123` 完成问答。
6. 打开管理员页面并使用 `admin / admin123` 查看系统概览、测试结果和日志。

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

默认模板面向 DeepSeek OpenAI-compatible 接口：

```powershell
$env:LLM_API_URL="https://api.deepseek.com/chat/completions"
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:LLM_MODEL_NAME="deepseek-v4-pro"
$env:LLM_PROVIDER="deepseek"
```

MiMo 模型使用：

```powershell
$env:MIMO_API_KEY="你的 MiMo API Key"
```

也可以在项目根目录创建 `.env.local`，内容参考 `.env.local.example`。`.env.local` 已被 `.gitignore` 排除，不能提交到仓库。

如需多模型配置，可使用 `LLM_PROVIDERS_JSON` 描述多个 provider，使用 `LLM_MODELS_JSON` 描述模型清单。上述字段只记录 provider、接口地址、模型名、上下文窗口和最大输出，不应写入密钥。管理员接口 `/api/admin/model-providers` 可查看当前 provider 配置，用户接口 `/api/models` 可查看可切换模型列表。

当前内置模型清单：

| Provider | 模型 | 别名 | 上下文窗口 | 最大输出 |
| --- | --- | --- | --- | --- |
| deepseek | `deepseek-v4-pro` | DS-Pro | 1,000K | 65,536 |
| deepseek | `deepseek-v4-flash` | DS-Flash | 1,000K | 65,536 |
| mimo | `mimo-v2.5-pro` | MiMo-Pro | 1,000K | 65,536 |
| mimo | `mimo-v2.5` | MiMo | 1,000K | 65,536 |

项目还提供轻量级知识库检索，默认读取 `knowledge_base/` 下的 Markdown 文件。问答命中知识库时，会把相关片段拼接到模型上下文中。重复问题会命中缓存，从而减少重复模型调用。

普通问答接口为 `/api/chat`，一次性返回完整 JSON，并支持请求体中的 `provider` 和 `model` 字段；流式问答接口为 `/api/chat/stream`，使用 Server-Sent Events 返回 `text/event-stream`，适合作为后续前端打字机式输出的扩展入口。多模型协作接口为 `/api/chat/collaborate`，按参与模型顺序生成多轮回答，再返回最终合成答案。

如果真实模型不可用，服务会自动回退到演示回答，并在日志中记录 `llm_remote_fallback`。管理员页面可通过日志说明系统具备失败降级能力，而不是直接中断主业务链路。

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
