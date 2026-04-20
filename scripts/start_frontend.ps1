param(
    [int]$Port = 5500
)

$python = "C:\Users\kidosto\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $python -m http.server $Port
