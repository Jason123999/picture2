$ErrorActionPreference = 'Stop'

param(
  [string]$BaseUrl = $(if ($env:API_BASE_URL) { $env:API_BASE_URL } else { 'http://127.0.0.1:8001/api' }),
  [string]$TenantSlug = $(if ($env:TENANT_SLUG) { $env:TENANT_SLUG } else { 'demo-tenant' }),
  [string]$Email = $(if ($env:ADMIN_EMAIL) { $env:ADMIN_EMAIL } else { 'admin@example.com' }),
  [string]$Password = $(if ($env:ADMIN_PASSWORD) { $env:ADMIN_PASSWORD } else { 'admin123456' })
)

$tokenResp = Invoke-RestMethod -Method POST -Uri "$BaseUrl/auth/token" -Headers @{ 'Content-Type'='application/x-www-form-urlencoded' } -Body "username=$Email&password=$Password&tenant_slug=$TenantSlug"
$token = $tokenResp.access_token
if (-not $token) { throw 'No access_token returned' }

$resp = Invoke-RestMethod -Method GET -Uri "$BaseUrl/admin/deploy-check" -Headers @{ 'Authorization' = "Bearer $token" }
Write-Host ($resp | ConvertTo-Json -Depth 10)
