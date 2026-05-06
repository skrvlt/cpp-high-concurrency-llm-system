# 基于 C++ 高并发架构与语言大模型的交互系统

这是一个面向计算机专业毕业设计交付的完整工程项目。项目目标不是只做一个静态页面或单脚本 Demo，而是把“前端交互、Python 智能服务、C++ 高并发网关、持久化、测试、压测证据、论文和答辩材料”整合在同一个仓库中，形成可运行、可验证、可讲解的毕业设计闭环。

当前版本已经完成：

- 用户登录、智能问答、历史记录、管理员概览、管理员日志、管理员配置维护。
- DeepSeek 与 MiMo 四个模型的可切换配置骨架。
- 普通问答、流式问答和多模型协作接口。
- 轻量级知识库检索、问答缓存和远程模型失败降级。
- SQLite 本地持久化验证和 MySQL 论文数据库结构设计。
- Linux / WSL 下的 C++ epoll 网关、转发、异常响应和压测证据。
- Windows + Linux + WSL 的运行说明、自动化测试、论文初稿、答辩材料。

## 一分钟理解项目

系统分为四层：

| 层级 | 目录 | 作用 | 是否跨平台 |
| --- | --- | --- | --- |
| 表现层 | `frontend/` | 用户端、管理员端静态页面，负责登录、问答、模型切换、历史和后台展示 | Windows / Linux / WSL |
| 智能服务层 | `services/ai_service/` | FastAPI 后端，负责认证、会话、模型调用、知识库、缓存、日志和配置 | Windows / Linux / WSL |
| 高并发接入层 | `cpp_gateway/` | C++17 + epoll 网关，负责 HTTP 接入、线程池处理和上游转发 | Linux / WSL |
| 数据与材料层 | `db/`、`output/`、`docs/` | 数据库结构、论文、图表、测试计划、答辩脚本和压测结果 | 文档与材料 |

运行策略是“两层支持”：

- 通用演示链路：前端 + Python API，正式支持 Windows、Linux、WSL。
- 高并发专项链路：C++ epoll 网关 + Python API，正式支持 Linux、WSL。

Windows 原生不承诺运行 epoll 网关，因为 epoll 是 Linux 内核机制；Windows 演示时使用直连 Python API，WSL/Linux 演示时可切换到 C++ 网关模式。

## 目录结构

```text
frontend/
  index.html            用户端页面
  admin.html            管理员页面
  app.js                登录、问答、历史、模型切换、多模型协作
  admin.js              后台概览、日志、配置、测试结果展示
  config.js             direct/gateway 前端接口模式配置
  styles.css            页面样式

services/ai_service/app/
  main.py               FastAPI 应用入口和 CORS 配置
  api.py                HTTP 路由层
  service.py            业务服务、模型调用、知识库、缓存、协作逻辑
  repository.py         Repository 抽象、内存仓储、SQLite 仓储
  models.py             请求/响应模型和领域对象

cpp_gateway/
  include/              C++ 网关头文件
  src/                  epoll HTTP 服务、线程池调用和上游转发
  CMakeLists.txt        CMake 构建文件
  README.md             C++ 网关专项说明

scripts/
  start_api.ps1         Windows 启动 Python API
  start_frontend.ps1    Windows 启动前端静态服务
  build_gateway_wsl.sh  WSL/Linux 构建 C++ 网关，缺 cmake 时回退 g++
  start_gateway_wsl.sh  WSL/Linux 启动 C++ 网关
  verify_runtime.*      验证健康检查、登录、问答主链路
  benchmark_gateway.py  网关压测脚本

db/
  schema.sql            论文使用的 MySQL 表结构设计

knowledge_base/
  project-notes.md      轻量知识库 Markdown 示例

tests/
  python/               Python API 和业务测试
  test_*.py             前端契约、C++ 网关、文档、压测、项目结构测试

docs/
  architecture.md       架构说明
  runbook.md            运行手册
  test-plan.md          测试方案
  gateway-validation.md 网关联调验证
  defense/              答辩脚本和问答备忘
  superpowers/plans/    项目模块路线图

output/
  doc/                  毕业设计说明书初稿 Markdown / DOCX / 图
  benchmark/            网关压测原始 JSON
  presentation/         答辩 PPT 大纲
```

## 环境要求

基础环境：

- Python 3.11+
- 浏览器
- Windows PowerShell 或 PowerShell 7
- Linux / WSL 用于 C++ epoll 网关
- 可选：CMake；没有 CMake 时脚本会回退到 `g++`

Python 依赖：

```powershell
python -m pip install -r requirements.txt
```

当前依赖包括：

- `fastapi`：Python API 框架
- `uvicorn[standard]`：API 服务启动器
- `httpx`：HTTP 测试/客户端能力
- `pydantic`：请求响应模型校验
- `python-docx`：论文 DOCX 生成和检查
- `pillow`：图像生成/验证

## 5 分钟验收路线

该路线不依赖真实 API Key，适合老师或陌生开发者快速确认项目可运行。

1. 安装依赖：

```powershell
python -m pip install -r requirements.txt
```

2. 启动 Python API：

```powershell
.\scripts\start_api.ps1
```

3. 打开健康检查：

```text
http://127.0.0.1:8000/api/health
```

正常返回应包含：

```json
{"status":"ok","service":"ai_service","runtime_mode":"demo","storage_mode":"memory"}
```

4. 新开终端启动前端：

```powershell
.\scripts\start_frontend.ps1
```

5. 打开用户端：

```text
http://127.0.0.1:5500/frontend/index.html
```

默认普通用户：

```text
student / student123
```

6. 打开管理员端：

```text
http://127.0.0.1:5500/frontend/admin.html
```

默认管理员：

```text
admin / admin123
```

## Windows 运行

Windows 下建议用于“前端 + Python API”主业务演示：

```powershell
.\scripts\start_api.ps1
.\scripts\start_frontend.ps1
```

可访问：

- `http://127.0.0.1:5500/frontend/index.html`
- `http://127.0.0.1:5500/frontend/admin.html`

Windows 原生不运行 C++ epoll 网关；如需验证网关，请使用 WSL。

## Linux / WSL 运行

启动 Python API：

```bash
bash scripts/start_api.sh
```

启动前端：

```bash
bash scripts/start_frontend.sh
```

构建 C++ 网关：

```bash
bash scripts/build_gateway_wsl.sh
```

启动 C++ 网关：

```bash
bash scripts/start_gateway_wsl.sh
```

网关模式前端：

```text
http://127.0.0.1:5500/frontend/index.html?mode=gateway
http://127.0.0.1:5500/frontend/admin.html?mode=gateway
```

网关验证：

```bash
bash scripts/verify_runtime.sh gateway
bash scripts/verify_gateway_smoke.sh
```

一键 WSL 联调：

```bash
bash scripts/validate_gateway_wsl.sh
```

`validate_gateway_wsl.sh` 支持：

- `API_MODE=local`：在 WSL 内部启动 Python API 后验证网关。
- `API_MODE=remote`：连接已经启动的外部 Python API。

## 核心接口

| 接口 | 方法 | 功能 |
| --- | --- | --- |
| `/api/health` | GET | 健康检查，返回运行模式、存储模式、模型名、会话数 |
| `/api/login` | POST | 用户登录，返回 token、角色、会话编号 |
| `/api/models` | GET | 返回可切换模型清单，不返回 API Key |
| `/api/chat` | POST | 普通问答，支持指定 `provider` 和 `model` |
| `/api/chat/stream` | POST | Server-Sent Events 流式问答 |
| `/api/chat/collaborate` | POST | 多模型协作问答 |
| `/api/history` | GET | 当前会话历史 |
| `/api/admin/overview` | GET | 管理员系统概览 |
| `/api/admin/logs` | GET | 管理员日志查看 |
| `/api/admin/config` | GET / POST | 管理员配置查询和更新 |
| `/api/admin/model-providers` | GET | 管理员查看模型供应商配置 |

## 模型接入

项目支持 OpenAI-compatible chat completions 调用。未配置 API Key 时，系统自动使用演示回答；真实模型调用失败时，会记录 `llm_remote_fallback` 日志并回退到演示回答，避免答辩现场主链路中断。

多模型配置采用“公开模型元数据 + 本地私密 Key”的方式：`.env.example` 保存可提交的默认运行配置，`.env.local.example` 保存本地 Key 模板，真正的 `.env.local` 只放在本机，不进入 Git。

内置模型清单：

| Provider | 模型 | 别名 | 上下文窗口 | 最大输出 |
| --- | --- | --- | --- | --- |
| deepseek | `deepseek-v4-pro` | DS-Pro | 1,000K | 65,536 |
| deepseek | `deepseek-v4-flash` | DS-Flash | 1,000K | 65,536 |
| mimo | `mimo-v2.5-pro` | MiMo-Pro | 1,000K | 65,536 |
| mimo | `mimo-v2.5` | MiMo | 1,000K | 65,536 |

真实 Key 不写入仓库。复制模板：

```powershell
Copy-Item .env.local.example .env.local
```

填写本地 `.env.local`：

```text
DEEPSEEK_API_KEY=你的 DeepSeek Key
MIMO_API_KEY=你的 MiMo Key
LLM_PROVIDER=deepseek
LLM_MODEL_NAME=deepseek-v4-pro
```

`.env.local` 已被 `.gitignore` 排除，不能提交。系统也支持直接读取系统环境变量；系统环境变量优先级高于 `.env.local`。

## 多模型协作

用户端有“模型选择”和“多模型协作”按钮：

- 普通发送：调用 `/api/chat`，只使用当前下拉框选中的模型。
- 多模型协作：调用 `/api/chat/collaborate`，按模型列表顺序让多个模型参考前一轮答案，再生成最终合成回答。

当前实现是“顺序协作式多模型问答”，不是完整生产级 Multi-Agent 平台。它已经具备多模型互相参考的答辩展示效果，但还没有复杂任务规划、工具调用、长期记忆和结果投票机制。

## 知识库和缓存

知识库：

- 默认读取 `knowledge_base/*.md`。
- 简单按查询词匹配 Markdown 内容。
- 命中后把片段作为参考上下文传给模型或演示回答逻辑。

缓存：

- 缓存 key 包含用户、provider、模型、问题和知识库上下文。
- 相同问题重复提问时复用回答，降低重复模型调用成本。
- 缓存命中不会重复写远程失败降级日志。

## 存储模式

默认：

```text
APP_STORAGE=memory
```

适合课堂演示和快速启动。

SQLite 持久化：

```powershell
$env:APP_STORAGE="sqlite"
$env:SQLITE_DB_PATH="runtime_data/app.sqlite3"
.\scripts\start_api.ps1
```

等价配置项写法是 `APP_STORAGE=sqlite`，启动后 `/api/health` 中的 `storage_mode` 会返回 `sqlite`。

SQLite 会保存会话、消息、日志和配置。`runtime_data/` 已被 `.gitignore` 排除。

论文中的正式数据库结构见：

```text
db/schema.sql
```

## C++ 网关实现

位置：

```text
cpp_gateway/src/http_server.cpp
```

关键实现：

- 使用 `epoll` 监听连接事件。
- 使用线程池处理请求。
- 按 `Content-Length` 读取完整 HTTP 请求体。
- 使用 `SendAll` 保证响应和转发请求完整写出。
- 将请求转发到 Python FastAPI 上游。
- 上游不可用时返回 `502 Bad Gateway` 风格 JSON。

定位：

- 这是毕业设计中的“Linux/WSL 高并发专项模块”。
- 当前重点证明 C++ 网络编程、epoll、转发和压测链路。
- 不是完整生产级 HTTP 网关。

## 测试

完整测试：

```powershell
python -m unittest discover -s tests -v
```

语法检查：

```powershell
python -m compileall services tests scripts tools
```

WSL 网关构建：

```bash
bash scripts/build_gateway_wsl.sh
```

当前已验证结果：

- `python -m unittest discover -s tests -v`：74 个测试通过，5 个中期检查固定文件名相关测试被条件跳过。
- `python -m compileall services tests scripts tools`：通过。
- WSL `bash scripts/build_gateway_wsl.sh`：通过，当前 WSL 缺少 `cmake` 时成功回退到 `g++`。
- 真实 FastAPI 进程启动并访问 `/api/health`：通过。

测试覆盖范围：

- API 登录、问答、历史、管理员接口。
- 模型列表、模型切换、多模型协作。
- 远程模型失败降级与缓存。
- SQLite 持久化。
- 前端契约和安全 DOM 渲染。
- C++ 网关源码结构和文档契约。
- 网关压测脚本和压测 JSON 结果。
- 论文 DOCX 生成、图表资产和文档结构。

## 压测证据

压测脚本：

```bash
python scripts/benchmark_gateway.py \
  --base-url http://127.0.0.1:8080 \
  --scenario health \
  --requests 1000 \
  --concurrency 100 \
  --output output/benchmark/gateway-health.json
```

聊天压测：

```bash
python scripts/benchmark_gateway.py \
  --base-url http://127.0.0.1:8080 \
  --scenario chat \
  --requests 300 \
  --concurrency 30 \
  --output output/benchmark/gateway-chat.json
```

已保留原始结果：

- `output/benchmark/gateway-health.json`
- `output/benchmark/gateway-chat.json`

管理员页面“测试结果”卡片会读取这些 JSON，展示成功率、吞吐量和 P95 响应时间。

## 论文和答辩材料

论文初稿：

- `output/doc/毕业设计说明书初稿.md`
- `output/doc/毕业设计说明书初稿.docx`

重新生成 DOCX：

```powershell
python tools/generate_thesis_docx.py
```

答辩材料：

- `docs/defense/demo-script.md`：五分钟演示脚本
- `docs/defense/qa-notes.md`：答辩问答备忘
- `output/presentation/答辩PPT大纲.md`：PPT 大纲

项目路线图：

- `docs/superpowers/plans/2026-04-28-graduation-project-module-roadmap.md`

## 当前可交付性判断

当前项目已经可以作为毕业设计工程交付，理由：

- 主业务链路可运行：登录、问答、历史、管理员概览、日志、配置均有接口和页面。
- 跨环境路径清晰：Windows 走通用演示链路，Linux/WSL 走 C++ epoll 网关链路。
- 代码有自动化测试支撑：API、服务、前端契约、网关、文档、压测材料均有测试。
- 论文和答辩材料已纳入仓库：不是只有代码，没有毕业设计说明材料。
- 高并发亮点可解释：C++ epoll 网关、线程池、完整请求读取、上游异常处理、压测 JSON 证据。
- LLM 亮点可演示：模型切换、DeepSeek/MiMo 配置、知识库上下文、多模型协作、失败降级。

## 已知问题和边界

这些不是当前交付阻断项，但答辩或后续开发需要清楚：

- 真实 API Key 不提交仓库，真实模型调用需要在本地 `.env.local` 或环境变量中配置。
- 当前未在测试日志中执行真实外部 API 调用，避免泄露 Key；自动化测试使用 demo/fallback 和 mock 验证接口链路。
- C++ 网关是毕业设计级高并发专项模块，不是完整生产级 HTTP 代理；暂不支持完整 keep-alive、HTTPS、复杂请求头策略和上传大文件。
- 多模型协作是顺序式协作，不是完整 Multi-Agent 框架；没有任务规划器、工具调用沙箱、长期记忆、投票仲裁和失败重试队列。
- 前端是静态页面，适合答辩演示；还没有复杂组件化工程、构建系统和前端单元测试。
- SQLite 是本地持久化验证；正式数据库设计以 `db/schema.sql` 的 MySQL 结构为论文依据。
- 中期检查材料目录中存在用户手工编辑和临时 Word 文件，最终工程测试已避免依赖固定中期文件名。

## 后续扩展建议

优先级建议：

| 优先级 | 扩展方向 | 价值 | 建议做法 |
| --- | --- | --- | --- |
| P0 | 保持当前交付稳定 | 避免答辩前引入风险 | 只修 bug、补截图、补演示脚本，不大改架构 |
| P1 | 真实 API 实网验收 | 让模型调用从“可配置”变成“已联调” | 在本地 `.env.local` 配 Key，跑一次真实 `/api/chat` 和 `/api/chat/collaborate` |
| P1 | 权限细化 | 管理端更完整 | 增加角色权限表、接口权限矩阵、前端权限隐藏 |
| P1 | RAG 增强 | 提升知识库亮点 | 支持文件上传、分段、向量检索、引用来源 |
| P2 | 多 Agent 调度 | 支撑更强扩展叙事 | 增加 Planner、Executor、Reviewer、Coordinator 四类 Agent |
| P2 | 第三方软件接入 | 扩展应用场景 | 接入微信、QQ、飞书等消息入口时先做适配层和权限控制 |
| P2 | 网关增强 | 提升工程深度 | keep-alive、连接池、限流、熔断、日志追踪 |
| P2 | Linux 服务器压测 | 增强性能实验说服力 | 在独立 Linux 服务器复现实验并保存环境参数 |

## 给陌生开发者的接手顺序

1. 先读本 README，理解四层架构和运行边界。
2. 执行 `python -m pip install -r requirements.txt`。
3. 执行 `python -m unittest discover -s tests -v`，确认本地环境正常。
4. 启动 `.\scripts\start_api.ps1`，访问 `/api/health`。
5. 启动 `.\scripts\start_frontend.ps1`，打开用户端和管理员端。
6. 阅读 `services/ai_service/app/service.py`，理解后端业务主流程。
7. 阅读 `frontend/app.js`，理解模型切换和多模型协作前端逻辑。
8. 在 WSL 中执行 `bash scripts/build_gateway_wsl.sh`，理解 C++ 网关链路。
9. 阅读 `docs/architecture.md`、`docs/runbook.md`、`docs/test-plan.md`。
10. 如要继续开发，先在路线图中新增模块，再建独立分支，不要直接混入论文或中期检查文件。
