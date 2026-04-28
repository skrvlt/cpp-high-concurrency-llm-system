param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8000
)

if ($env:PYTHON) {
    $python = $env:PYTHON
    $pythonArgs = @()
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $python = "py"
    $pythonArgs = @("-3")
} else {
    $python = "python"
    $pythonArgs = @()
}

& $python @pythonArgs -m uvicorn services.ai_service.app.main:app --host $HostAddress --port $Port
