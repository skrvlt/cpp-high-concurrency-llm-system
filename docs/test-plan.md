# 测试方案

## 测试目标

验证以下内容：

1. 用户登录是否成功
2. 聊天接口是否返回答案
3. 历史记录是否正确保存
4. 日志接口是否返回事件列表
5. 配置接口是否支持查询与更新
6. SQLite 仓储是否能够持久化会话、日志和配置
7. 项目关键目录与文档是否齐全
8. 远程模型失败时是否记录降级日志
9. 知识库检索、问答缓存、流式输出和多模型配置接口是否可用

## 测试层次

### 单元测试

- `tests/python/test_service.py`
- `tests/python/test_api.py`

其中 `test_sqlite_repository_persists_sessions_config_and_logs` 用项目内临时 SQLite 文件验证持久化链路，覆盖会话消息、系统配置和日志记录。

P1/P2 增强测试覆盖以下内容：

- `test_remote_model_failure_is_logged_as_fallback`：远程模型异常时返回演示答案并记录 `llm_remote_fallback` 日志。
- `test_knowledge_base_returns_matching_context`：验证 `knowledge_base/` Markdown 资料可被检索。
- `test_chat_uses_response_cache_for_repeated_question`：验证重复问题命中缓存，避免重复模型调用。
- `test_cached_answer_does_not_log_remote_fallback_again`：验证缓存命中不会重复记录远程模型降级日志。
- `test_chat_stream_endpoint_returns_text_event_stream`：验证 `/api/chat/stream` 返回 `text/event-stream`。
- `test_admin_can_read_model_providers`：验证管理员可查看多模型配置清单。
- `test_cors_origin_policy_is_configurable`：验证 CORS 来源由 `APP_CORS_ORIGINS` 控制，而不是全开放。

运行 Python 接口测试前需要安装依赖：

```bash
python -m pip install -r requirements.txt
```

持久化相关测试覆盖 `APP_STORAGE=sqlite`、SQLite 会话恢复、配置恢复、日志恢复，以及 `/api/health` 中的 `storage_mode` 字段。

### 结构测试

- `tests/test_project_layout.py`
- `tests/test_frontend_contract.py`
- `tests/test_cpp_gateway_layout.py`
- `tests/test_docs.py`

## 并发测试建议

建议在 Linux 或 WSL 环境启动 Python 服务和 C++ 网关后，使用项目自带脚本进行可复现压测：

```bash
python scripts/benchmark_gateway.py \
  --base-url http://127.0.0.1:8080 \
  --scenario health \
  --requests 1000 \
  --concurrency 100 \
  --output output/benchmark/gateway-health.json
```

如需测试完整问答链路，可执行：

```bash
python scripts/benchmark_gateway.py \
  --base-url http://127.0.0.1:8080 \
  --scenario chat \
  --requests 300 \
  --concurrency 30 \
  --output output/benchmark/gateway-chat.json
```

脚本会输出并落盘以下指标：

- 平均响应时间
- P95 响应时间
- 吞吐量
- 错误率
- `throughput_rps`
- `success_rate_percent`
- 错误样例

`ab` 可作为补充工具，但论文第 6 章建议优先引用 `scripts/benchmark_gateway.py` 生成的 JSON 结果，便于保留实验参数和原始指标。

## M6 实测结果

本阶段在 Windows + WSL 联调环境下完成 C++ 网关真实压测。Python FastAPI 服务运行在 `127.0.0.1:8000`，C++ epoll 网关运行在 WSL 中。由于本机 `8080` 端口被其他服务占用，本次压测将网关端口设置为 `18081`，上游仍指向 `127.0.0.1:8000`。

压测前发现 C++ 网关在并发 POST 场景下存在请求体读取不完整的问题，表现为少量 `422 Unprocessable Entity` 和连接重置。修复方式为按照 `Content-Length` 循环读取完整 HTTP 请求体后再转发给 Python 服务。修复后实测结果如下：

| 场景 | 总请求数 | 并发数 | 平均响应时间/ms | P95 响应时间/ms | throughput_rps | 成功率/% | 错误数 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| health | 1000 | 100 | 134.21 | 166.90 | 635.41 | 100.00 | 0 |
| chat | 300 | 30 | 43.67 | 65.21 | 642.10 | 100.00 | 0 |

原始 JSON 结果保存位置：

- `output/benchmark/gateway-health.json`
- `output/benchmark/gateway-chat.json`

管理员前端的“测试结果”卡片会读取上述 JSON 文件，展示成功率、吞吐量和 P95 响应时间，便于答辩现场直接说明压测证据。

## P1/P2 回归验证命令

完成 P1/P2 增强后，至少执行以下命令：

```powershell
python -m unittest discover -s tests -v
python -m compileall services tests scripts tools
```

如果当前机器可用 WSL 或 Linux，还应执行：

```bash
bash scripts/build_gateway_wsl.sh
```

以上命令分别验证 Python API、服务层缓存与降级、前端契约、文档契约、C++ 网关结构和脚本语法。WSL 构建用于确认 `SendAll` 等网关改动不会破坏 Linux/WSL 编译链路。
