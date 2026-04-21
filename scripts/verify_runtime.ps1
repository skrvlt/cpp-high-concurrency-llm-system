param(
    [ValidateSet("direct", "gateway")]
    [string]$Mode = "direct",
    [string]$HostAddress = "127.0.0.1",
    [int]$ApiPort = 8000,
    [int]$GatewayPort = 8080
)

$port = if ($Mode -eq "gateway") { $GatewayPort } else { $ApiPort }
$baseUri = "http://$HostAddress`:$port/api"

Write-Output "Verify mode: $Mode"
Write-Output "Base URI: $baseUri"

$health = Invoke-RestMethod -Method Get -Uri "$baseUri/health"
Write-Output "Health response:"
$health | ConvertTo-Json -Depth 5

$loginResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$baseUri/login" `
  -ContentType "application/json" `
  -Body '{"username":"student","password":"student123"}'

Write-Output "Login response:"
$loginResponse | ConvertTo-Json -Depth 5

$token = $loginResponse.token

$chatResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$baseUri/chat" `
  -ContentType "application/json" `
  -Body (@{ token = $token; message = "请返回当前运行模式的验证信息" } | ConvertTo-Json)

Write-Output "Chat response:"
$chatResponse | ConvertTo-Json -Depth 5
