$ErrorActionPreference = 'Stop'

$Port = if ($env:BACKEND_PORT) { [int]$env:BACKEND_PORT } else { 8001 }

try {
  $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/health" -Method GET -TimeoutSec 5
  Write-Host "Health:" ($resp | ConvertTo-Json -Compress)
} catch {
  Write-Host "Health check failed:" $_
  exit 1
}
