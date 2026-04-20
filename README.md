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

## 运行方式

### Windows

```powershell
.\scripts\start_api.ps1
.\scripts\start_frontend.ps1
```

前端默认直连 Python 服务：

- `http://127.0.0.1:5500/frontend/index.html`
- `http://127.0.0.1:5500/frontend/admin.html`

### Linux / WSL

```bash
bash scripts/start_api.sh
bash scripts/start_frontend.sh
bash scripts/build_gateway_wsl.sh
```

如果需要通过网关访问前端，可使用：

- `http://127.0.0.1:5500/frontend/index.html?mode=gateway`
- `http://127.0.0.1:5500/frontend/admin.html?mode=gateway`

## 真实大模型接口

未配置环境变量时，系统使用演示模式回答；配置后可接真实模型：

- `LLM_API_URL`
- `LLM_API_KEY`
- `LLM_MODEL_NAME`

## 默认账号

- 管理员：`admin / admin123`
- 普通用户：`student / student123`
