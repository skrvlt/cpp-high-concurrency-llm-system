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

## 默认账号

- 管理员：`admin / admin123`
- 普通用户：`student / student123`
