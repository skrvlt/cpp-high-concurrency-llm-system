# 网关验证说明

该文档用于指导 Linux / WSL 环境下的 C++ epoll 网关验证。

## 目标

验证以下内容：

1. `cpp_gateway` 在 WSL 或 Linux 下可编译
2. 网关启动后监听 `8080`
3. Python 服务启动后，网关可将请求转发到 `8000`
4. `/api/login`、`/api/chat`、`/api/history` 主链路通过网关可用
5. 上游服务未启动时，网关返回明确错误

## 启动顺序

1. 启动 Python 服务
2. 启动前端静态服务
3. 编译并启动 C++ 网关
4. 使用浏览器的 `?mode=gateway` 或 curl 执行验证

## 关键验证命令

### 登录

```bash
curl -X POST http://127.0.0.1:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}'
```

### 问答

```bash
curl -X POST http://127.0.0.1:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"token":"<token>","message":"通过网关提问"}'
```

### 历史记录

```bash
curl "http://127.0.0.1:8080/api/history?token=<token>"
```

## 结果要求

- 网关可成功转发 `/api/chat`
- `/api/history` 返回会话标题和消息列表
- 当 Python 服务关闭时，网关返回 `502 Bad Gateway` 风格错误响应
