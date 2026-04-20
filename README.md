# 基于 C++ 高并发架构与语言大模型的交互系统

这是毕业设计第一版成品仓库，包含以下内容：

- `frontend/`：用户端和管理员端静态页面
- `services/ai_service/`：Python FastAPI 智能服务层
- `cpp_gateway/`：Linux C++ 高并发接入层示例实现
- `db/schema.sql`：MySQL 数据库结构
- `output/doc/`：毕业设计说明书初稿
- `docs/`：架构、运行和测试说明

## 第一版功能

- 用户登录
- 智能问答
- 多轮历史对话
- 管理员查看日志
- 管理员查看和修改系统配置
- MySQL 表结构设计
- Linux C++ 网关架构与代码骨架

## 快速运行

### 1. 启动 Python 服务

```powershell
C:\Users\kidosto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m uvicorn services.ai_service.app.main:app --host 127.0.0.1 --port 8000
```

### 2. 打开前端页面

直接在浏览器中打开：

- `frontend/index.html`
- `frontend/admin.html`

如果需要通过本地静态服务器打开，可在仓库根目录运行：

```powershell
python -m http.server 5500
```

### 3. 默认账号

- 管理员：`admin / admin123`
- 普通用户：`student / student123`

## 说明

- Python 服务默认使用内存仓储，方便本地演示与测试。
- Python 服务支持两种模型模式：
  - 默认演示模式：未配置环境变量时返回可控的演示回答
  - 真实接口模式：配置 `LLM_API_URL`、`LLM_API_KEY`、`LLM_MODEL_NAME` 后调用远程大模型
- 如果补充 MySQL 连接层，可直接复用 `db/schema.sql`。
- C++ 网关面向 Linux 环境，当前仓库给出完整骨架、基础 HTTP 解析、线程池和向 Python 服务的转发逻辑。
