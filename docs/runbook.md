# 运行说明

## 环境要求

- Python 3.11+
- FastAPI、uvicorn
- 浏览器
- Linux 环境用于编译和运行 C++ 网关

## Python 服务启动

```powershell
C:\Users\kidosto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m uvicorn services.ai_service.app.main:app --host 127.0.0.1 --port 8000
```

## 真实大模型接口配置

如果需要让系统调用真实大模型，而不是使用演示回复，在启动前设置以下环境变量：

```powershell
$env:LLM_API_URL="https://your-model-endpoint/v1/chat/completions"
$env:LLM_API_KEY="your-api-key"
$env:LLM_MODEL_NAME="your-model-name"
```

未配置时，系统会自动退回演示模式，便于答辩时稳定展示。

## 前端访问

直接打开：

- `frontend/index.html`
- `frontend/admin.html`

如果浏览器阻止本地文件的接口访问，可改用静态文件服务：

```powershell
python -m http.server 5500
```

然后访问：

- `http://127.0.0.1:5500/frontend/index.html`
- `http://127.0.0.1:5500/frontend/admin.html`

## Linux C++ 网关编译

```bash
cd cpp_gateway
mkdir -p build
cd build
cmake ..
make
./llm_gateway
```

当前网关会监听 `8080` 端口，并将 `/api/*` 请求转发到 `127.0.0.1:8000` 的 Python 服务。

## 默认账号

- 管理员：`admin / admin123`
- 普通用户：`student / student123`
