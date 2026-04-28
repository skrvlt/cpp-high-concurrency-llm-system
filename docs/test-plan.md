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

## 测试层次

### 单元测试

- `tests/python/test_service.py`
- `tests/python/test_api.py`

其中 `test_sqlite_repository_persists_sessions_config_and_logs` 用项目内临时 SQLite 文件验证持久化链路，覆盖会话消息、系统配置和日志记录。

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

后续在 Linux 环境使用以下命令：

```bash
ab -n 1000 -c 100 http://127.0.0.1:8080/api/chat
```

记录指标：

- 平均响应时间
- 吞吐量
- 错误率
- 并发数变化趋势
