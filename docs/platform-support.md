# 跨环境支持说明

本项目按照“整套项目跨平台，C++ epoll 网关作为 Linux/WSL 专项实现”的原则设计。

## 支持矩阵

| 环境 | 前端 | Python 服务 | C++ 网关 | 说明 |
| --- | --- | --- | --- | --- |
| Windows | 支持 | 支持 | 不作为原生目标 | 适合开发、论文撰写、界面演示 |
| WSL | 支持 | 支持 | 支持 | 适合在 Windows 主机上完成 Linux 风格联调 |
| Linux | 支持 | 支持 | 支持 | 适合正式部署和后续高并发压测 |

## 运行模式

### Windows 演示模式

- 直接启动 Python 服务
- 打开前端静态页面或使用本地静态服务器
- 前端默认直连 `http://127.0.0.1:8000/api`
- 可通过 `scripts/verify_runtime.ps1 -Mode direct` 验证 `/api/health`、登录与问答链路

### WSL 联调模式

- 在 WSL 中编译并启动 `cpp_gateway`
- Python 服务可运行在 Windows 或 WSL，但端口与访问地址需要保持一致
- 前端可以切换为 `gateway` 模式，经 `http://127.0.0.1:8080/api` 访问后端
- 可通过 `bash scripts/verify_runtime.sh gateway` 验证 `/api/health` 与经网关转发的主链路

### Linux 部署模式

- 启动 Python 服务
- 编译并启动 C++ 网关
- 前端通过静态文件服务或 Nginx 提供访问
- 后续高并发压测建议在该环境完成
- 建议先参考根目录 `.env.example` 完成环境变量与端口约定

## 关键约束

- `Python 服务`统一使用 `8000` 端口。
- `C++ 网关`统一使用 `8080` 端口。
- 统一健康检查接口为 `/api/health`。
- `epoll` 是 Linux 专属机制，因此 C++ 网关不承诺 Windows 原生可运行。
- Windows、Linux、WSL 共享同一套前端和 Python 服务接口契约。
