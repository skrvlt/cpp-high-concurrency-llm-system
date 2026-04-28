param(
    [int]$Port = 5500
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

& $python @pythonArgs -m http.server $Port
