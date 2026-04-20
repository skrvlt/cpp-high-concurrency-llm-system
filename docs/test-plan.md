# 测试方案

## 测试目标

验证以下内容：

1. 用户登录是否成功
2. 聊天接口是否返回答案
3. 历史记录是否正确保存
4. 日志接口是否返回事件列表
5. 配置接口是否支持查询与更新
6. 项目关键目录与文档是否齐全

## 测试层次

### 单元测试

- `tests/python/test_service.py`
- `tests/python/test_api.py`

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
