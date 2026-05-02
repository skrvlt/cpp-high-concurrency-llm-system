# 毕业设计答辩演示脚本

本文档用于答辩现场按固定顺序演示项目，目标是在 5 分钟内证明系统能运行、能交互、能管理、能通过 C++ 网关联调，并且有测试与压测证据。

## 1. 演示前准备

进入项目根目录：

```powershell
cd C:\Users\kidosto\Desktop\校内相关\毕业相关\毕业设计
python -m pip install -r requirements.txt
```

如果只演示 Windows 通用链路，启动 Python API 和前端：

```powershell
.\scripts\start_api.ps1
.\scripts\start_frontend.ps1
```

对应脚本文件为 `scripts/start_api.ps1` 和 `scripts/start_frontend.ps1`。

检查 Python 服务是否可访问：

```text
http://127.0.0.1:8000/api/health
```

页面返回 `status`、`runtime_mode`、`storage_mode`、`model_name`、`session_count` 等字段，说明后端 API 已正常启动。

## 2. 用户端演示流程

打开前端页面：

```text
http://127.0.0.1:5500/frontend/index.html
```

演示顺序：

1. 展示页面顶部运行状态，说明当前前端直连 Python 服务。
2. 使用普通用户登录，说明系统具备基础身份识别能力。
3. 在问答框输入一个问题，例如“请说明 Reactor 模式在本系统中的作用”。
4. 提交问题后展示回答结果，说明前端、后端接口和模型封装链路已经贯通。
5. 打开历史记录区域，展示系统保存了会话内容。

## 3. 管理端演示流程

打开后台页面：

```text
http://127.0.0.1:5500/frontend/admin.html
```

演示顺序：

1. 使用管理员账号登录。
2. 展示系统概览，包括用户数、会话数、消息数、日志数和模型名称。
3. 展示日志列表，说明登录、问答和配置修改行为会被记录。
4. 修改模型配置项，说明系统具有后台维护能力。

## 4. C++ 网关模式演示

WSL 或 Linux 环境下构建并启动 C++ 网关：

```bash
bash scripts/build_gateway_wsl.sh
bash scripts/start_gateway_wsl.sh
```

如果 8080 端口被占用，可以改用临时端口：

```bash
GATEWAY_PORT=18081 UPSTREAM_HOST=127.0.0.1 UPSTREAM_PORT=8000 bash scripts/start_gateway_wsl.sh
```

前端切换到网关模式：

```text
http://127.0.0.1:5500/frontend/index.html?mode=gateway
```

说明重点：

1. 普通模式用于 Windows 快速演示。
2. `?mode=gateway` 用于展示前端请求经 C++ epoll 网关转发。
3. C++ 网关是 Linux/WSL 专项模块，不承诺 Windows 原生运行 epoll。

## 5. 测试与压测证据展示

展示完整测试命令：

```powershell
python -m unittest discover -s tests -v
python -m compileall services tests scripts tools
```

展示压测结果文件：

```text
output/benchmark/gateway-health.json
output/benchmark/gateway-chat.json
```

可说明的结果：

1. health 场景 1000 次请求、100 并发、成功率 100%。
2. chat 场景 300 次请求、30 并发、成功率 100%。
3. 压测曾发现并发 POST 请求体读取不完整问题，已经通过按 Content-Length 读取完整请求体修复。

## 6. 结束语

本系统的核心价值是把 C++ 高并发接入能力与 Python 大语言模型服务封装能力结合起来。C++ 网关负责连接接入、请求读取和转发，Python 服务负责业务接口、会话管理、模型调用和持久化，前端负责用户交互与后台展示。整体工程已经形成 Windows 通用演示、WSL 网关联调、Linux 部署压测三类运行路径。
