$ErrorActionPreference = 'Stop'

param(
  [string]$BaseUrl = $(if ($env:API_BASE_URL) { $env:API_BASE_URL } else { 'http://127.0.0.1:8001/api' }),
  [string]$LoginTenantSlug = $(if ($env:LOGIN_TENANT_SLUG) { $env:LOGIN_TENANT_SLUG } else { 'demo-tenant' }),
  [string]$Email = $(if ($env:ADMIN_EMAIL) { $env:ADMIN_EMAIL } else { 'admin@example.com' }),
  [string]$Password = $(if ($env:ADMIN_PASSWORD) { $env:ADMIN_PASSWORD } else { 'admin123456' }),

  [Parameter(Mandatory=$true)][string]$TenantSlug,
  [Parameter(Mandatory=$true)][string]$TenantName,
  [Parameter(Mandatory=$true)][string]$TenantAdminEmail,
  [Parameter(Mandatory=$true)][string]$TenantAdminPassword
)

$tokenResp = Invoke-RestMethod -Method POST -Uri "$BaseUrl/auth/token" -Headers @{ 'Content-Type'='application/x-www-form-urlencoded' } -Body "username=$Email&password=$Password&tenant_slug=$LoginTenantSlug"
$token = $tokenResp.access_token
if (-not $token) { throw 'No access_token returned' }

$payload = @{ tenant_name=$TenantName; tenant_slug=$TenantSlug; admin_email=$TenantAdminEmail; admin_password=$TenantAdminPassword } | ConvertTo-Json
$resp = Invoke-RestMethod -Method POST -Uri "$BaseUrl/admin/provision" -Headers @{ 'Authorization' = "Bearer $token"; 'Content-Type'='application/json' } -Body $payload

Write-Host ($resp | ConvertTo-Json -Depth 10)
if ($resp.site_url) { Write-Host "site_url: $($resp.site_url)" }
if ($resp.site_url_stable) { Write-Host "site_url_stable: $($resp.site_url_stable)" }
if ($resp.site_url_immediate) { Write-Host "site_url_immediate: $($resp.site_url_immediate)" }
if ($resp.deployment_url) { Write-Host "deployment_url: $($resp.deployment_url)" }
