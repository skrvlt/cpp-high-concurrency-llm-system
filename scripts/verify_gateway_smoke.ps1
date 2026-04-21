[CmdletBinding()]
param(
    [string]$HostAddress = "127.0.0.1",
    [int]$GatewayPort = 8080
)

$baseUri = "http://$HostAddress`:$GatewayPort/api"

Write-Output "Health response:"
Invoke-RestMethod `
  -Method Get `
  -Uri "$baseUri/health"

$loginResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$baseUri/login" `
  -ContentType "application/json" `
  -Body '{"username":"student","password":"student123"}'

Write-Output "Login response:"
$loginResponse | ConvertTo-Json -Depth 5

$token = $loginResponse.token

Write-Output "Chat response:"
Invoke-RestMethod `
  -Method Post `
  -Uri "$baseUri/chat" `
  -ContentType "application/json" `
  -Body (@{ token = $token; message = "请通过网关回答当前系统目标" } | ConvertTo-Json)

Write-Output "History response:"
Invoke-RestMethod `
  -Method Get `
  -Uri ($baseUri + "/history?token=" + $token)
