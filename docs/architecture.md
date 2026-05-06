# 系统架构说明

## 总体结构

系统采用四层架构：

1. 表现层：浏览器页面，负责登录、问答、历史记录和管理员查看。
2. 接入层：Linux C++ 网关，负责 HTTP 接入、epoll 事件分发、线程池和请求转发。
3. 智能服务层：Python FastAPI 服务，负责认证、聊天、日志、配置、知识库检索、缓存、流式输出和模型调用。
4. 数据层：仓储接口屏蔽具体存储方式，默认使用内存仓储便于演示，也可通过 SQLite 仓储验证用户、会话、消息、日志和配置的持久化；MySQL 表结构用于正式数据库设计说明。

## 请求链路

1. 用户在前端提交登录或提问请求。
2. C++ 网关接收 HTTP 请求并放入线程池处理。
3. 网关将业务请求转发到 Python 智能服务层。
4. Python 服务校验 token、检索知识库上下文、组织 Prompt、调用模型客户端并生成响应。
5. 会话与日志被写入仓储层。
6. 结果返回 C++ 网关，再返回浏览器。

## 模块划分

### frontend

- `index.html`：用户主页面
- `admin.html`：管理员页面
- `app.js`：用户端逻辑
- `admin.js`：管理员端逻辑
- `styles.css`：统一样式

### services/ai_service

- `models.py`：请求、响应和领域模型
- `repository.py`：内存仓储
- `service.py`：认证、问答、日志业务、知识库检索、问答缓存，以及“远程模型调用/本地演示回退”逻辑
- `api.py`：FastAPI 路由
- `main.py`：应用入口

仓储层通过统一方法暴露用户、会话、日志和配置读写能力。`APP_STORAGE=memory` 时使用进程内数据结构，`APP_STORAGE=sqlite` 时使用本地 SQLite 文件，二者对上层服务保持相同接口。服务健康检查通过 `storage_mode` 暴露当前存储模式，便于跨环境演示和部署验证。

模型接入层采用 OpenAI-compatible 请求格式，`.env.example` 默认提供 DeepSeek `deepseek-v4-flash` 配置模板。系统未配置 API Key 时保持演示模式；配置 `LLM_API_URL`、`LLM_API_KEY`、`LLM_MODEL_NAME` 后可调用真实模型。`LLM_PROVIDERS_JSON` 用于描述多模型配置清单，管理员可通过 `/api/admin/model-providers` 查看 provider 信息。知识库检索默认读取 `knowledge_base/` 下的 Markdown 文件，重复问题会命中服务层缓存。

服务层同时保留普通问答接口和流式问答接口：`/api/chat` 用于稳定返回完整 JSON，`/api/chat/stream` 使用 Server-Sent Events 输出 `text/event-stream`。该设计保证当前答辩演示链路简单稳定，同时给后续前端逐字输出、多 Agent 中间状态展示和长回答生成保留扩展入口。

跨域访问采用环境变量 `APP_CORS_ORIGINS` 管理，不再使用全开放来源配置。默认只允许本地前端静态服务地址访问，部署到其他主机时通过环境变量追加实际前端地址。

### cpp_gateway

- `main.cpp`：程序入口
- `http_server.cpp`：epoll 事件循环、HTTP 请求解析、完整缓冲区发送和上游转发
- `thread_pool.h`：简化线程池
- `http_server.h`：网关接口

C++ 网关的响应发送统一经过 `SendAll` 完成，避免并发或大响应场景下出现短写导致响应体不完整。网关仍定位为 Linux/WSL 高并发专项模块，不承诺 Windows 原生 epoll 实现。

## 论文对应关系

- 第 3 章 系统需求分析：对应前端角色、系统功能和业务流程
- 第 4 章 系统总体设计：对应四层结构、数据库和模块设计
- 第 5 章 系统详细实现：对应前端、Python 服务、C++ 网关代码
- 第 6 章 系统测试：对应接口测试、功能测试和并发测试
