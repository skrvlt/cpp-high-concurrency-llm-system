# Linux C++ 高并发接入层

该目录提供毕业设计第一版的 C++ 网关代码骨架，目标环境为 Linux。

## 功能

- 监听 HTTP 连接
- 使用 epoll 管理事件
- 使用线程池处理任务
- 解析基础 HTTP 报文
- 将业务请求转发到 Python FastAPI 服务

## 编译

```bash
mkdir -p build
cd build
cmake ..
make
```

## 说明

当前版本重点是毕业设计成品的完整性与结构清晰度，后续可以继续增强：

- 更完整的 HTTP 解析
- keep-alive
- 更稳定的错误处理
- 压测优化
- 转发时采用更稳健的客户端实现
