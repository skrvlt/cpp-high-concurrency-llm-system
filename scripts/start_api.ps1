param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8000
)

$python = "C:\Users\kidosto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $python -m uvicorn services.ai_service.app.main:app --host $HostAddress --port $Port
