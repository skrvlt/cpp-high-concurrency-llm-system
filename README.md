# 基于 C++ 高并发架构与语言大模型的交互系统

这是毕业设计项目仓库，当前版本已经具备完整的代码、论文初稿、测试、运行文档与参考资料整理结构。

## 项目结构

- `frontend/`：用户端和管理员端静态页面
- `services/ai_service/`：Python FastAPI 智能服务层
- `cpp_gateway/`：Linux/WSL 下的 C++ epoll 高并发接入层
- `db/schema.sql`：MySQL 数据库结构设计
- `output/doc/`：毕业设计说明书初稿
- `docs/`：架构、运行、测试与跨环境说明
- `scripts/`：Windows、Linux、WSL 启动与构建脚本
- `references/`：开题报告、学校模板、图表示例和外部参考毕设资料

## 核心功能

- 用户登录
- 智能问答
- 多轮历史对话
- 管理员系统概览
- 管理员日志查看
- 管理员配置更新
- Linux/WSL 下的 C++ 网关转发

## 跨环境支持策略

本项目采用“两层支持目标”：

- `通用层`：前端 + Python 服务，正式支持 Windows、Linux、WSL
- `高并发专项层`：C++ epoll 网关，正式支持 Linux、WSL

也就是说，项目整体是跨环境可运行的，但 `epoll` 网关不以 Windows 原生运行为目标。

## 统一端口

- Python 服务：`8000`
- C++ 网关：`8080`
- 前端静态服务：默认 `5500`

## 环境变量模板

项目根目录提供 `.env.example`，用于统一约定模型接口地址、运行端口和网关参数。

- `LLM_API_URL`
- `LLM_API_KEY`
- `LLM_MODEL_NAME`
- `LLM_PROVIDER`
- `LLM_PROVIDERS_JSON`
- `APP_CORS_ORIGINS`
- `APP_STORAGE`
- `SQLITE_DB_PATH`
- `API_PORT`
- `FRONTEND_PORT`
- `GATEWAY_PORT`
- `UPSTREAM_HOST`
- `UPSTREAM_PORT`

## Python 依赖安装

首次运行 Python 服务或测试前，在项目根目录执行：

```powershell
python -m pip install -r requirements.txt
```

Linux / WSL 下同样使用：

```bash
python -m pip install -r requirements.txt
```

## 运行方式

## 5 分钟验收路线

1. 执行 `python -m pip install -r requirements.txt` 安装依赖。
2. 执行 `.\scripts\start_api.ps1` 启动 Python API。
3. 打开 `http://127.0.0.1:8000/api/health`，确认服务返回 `status=ok`。
4. 执行 `.\scripts\start_frontend.ps1` 启动前端静态服务。
5. 打开 `http://127.0.0.1:5500/frontend/index.html`，使用 `student / student123` 登录并提问。
6. 打开 `http://127.0.0.1:5500/frontend/admin.html`，使用 `admin / admin123` 查看系统概览、测试结果和日志。

该路线不依赖外部 API Key，适合教师快速验收项目是否可运行。

### Windows

```powershell
.\scripts\start_api.ps1
.\scripts\start_frontend.ps1
.\scripts\verify_runtime.ps1 -Mode direct
```

前端默认直连 Python 服务：

- `http://127.0.0.1:5500/frontend/index.html`
- `http://127.0.0.1:5500/frontend/admin.html`

### Linux / WSL

```bash
bash scripts/start_api.sh
bash scripts/start_frontend.sh
bash scripts/build_gateway_wsl.sh
bash scripts/start_gateway_wsl.sh
bash scripts/verify_runtime.sh direct
```

如果需要通过网关访问前端，可使用：

- `http://127.0.0.1:5500/frontend/index.html?mode=gateway`
- `http://127.0.0.1:5500/frontend/admin.html?mode=gateway`

网关模式验证命令：

```bash
bash scripts/verify_runtime.sh gateway
bash scripts/verify_gateway_smoke.sh
```

## 健康检查接口

统一健康检查接口为 `/api/health`，返回服务状态、运行模式、存储模式、模型名称和会话数量，可用于三类环境下的最小可运行验证。其中 `storage_mode` 用于区分当前是 `memory` 还是 `sqlite`。

## 稳定接口

当前版本保持以下接口契约稳定：

- `/api/login`：用户登录，返回 token、角色和会话编号。
- `/api/chat`：普通问答接口，返回完整回答。
- `/api/chat/stream`：Server-Sent Events 流式问答接口，返回 `text/event-stream`。
- `/api/history`：返回当前会话历史记录。
- `/api/admin/logs`：管理员查看运行日志。
- `/api/admin/config`：管理员查看或修改模型配置。
- `/api/admin/overview`：管理员查看系统概览。
- `/api/admin/model-providers`：管理员查看多模型配置清单。

## 真实大模型接口

未配置 API Key 时，系统使用演示模式回答；配置后可接真实模型。默认模板采用 DeepSeek 的 OpenAI-compatible chat completions 形式：

- `LLM_API_URL`
- `LLM_API_KEY`
- `LLM_MODEL_NAME`
- `LLM_PROVIDER`
- `LLM_PROVIDERS_JSON`

`.env.example` 默认给出 `https://api.deepseek.com/chat/completions` 和 `deepseek-v4-flash`。如果要接入其他 OpenAI-compatible 服务，只需要替换 URL、Key 和模型名。系统支持多模型配置骨架：可通过 `LLM_PROVIDERS_JSON` 声明多个 provider，后台接口 `/api/admin/model-providers` 会返回当前模型配置清单。

`APP_CORS_ORIGINS` 用于限制允许访问 Python API 的前端来源，默认允许 `127.0.0.1:5500` 和 `localhost:5500`。如果部署到其他地址，应把实际前端地址加入该变量，而不是恢复为全开放配置。

## 知识库检索与缓存

项目提供轻量级知识库检索能力，默认读取 `knowledge_base/` 下的 Markdown 文件。用户提问命中知识库内容时，系统会把相关片段作为参考资料传给模型或演示回答逻辑。系统还提供问答缓存，同一用户、同一模型、同一问题和同一知识库上下文会复用已生成回答，降低重复调用成本。远程模型调用失败时，系统会返回演示回答并写入 `llm_remote_fallback` 日志，便于管理员页面解释降级原因。

## 数据存储模式

默认 `APP_STORAGE=memory`，适合课堂演示和快速启动；如需验证会话、日志和配置的持久化，可设置 `APP_STORAGE=sqlite`：

```powershell
$env:APP_STORAGE="sqlite"
$env:SQLITE_DB_PATH="runtime_data/app.sqlite3"
```

Linux / WSL 下使用：

```bash
export APP_STORAGE=sqlite
export SQLITE_DB_PATH=runtime_data/app.sqlite3
```

SQLite 模式会在本地生成运行数据库，接口契约与内存模式保持一致。

## 默认账号

- 管理员：`admin / admin123`
- 普通用户：`student / student123`
