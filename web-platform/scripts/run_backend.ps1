$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$VenvPython = Join-Path $Root '.venv\Scripts\python.exe'

if (-not (Test-Path $VenvPython)) {
  throw "Python venv not found: $VenvPython"
}

# Allow overriding port via env var
$Port = if ($env:BACKEND_PORT) { [int]$env:BACKEND_PORT } else { 8001 }

# Ensure module discovery works regardless of current directory
$env:PYTHONPATH = $Backend
Set-Location $Backend

Write-Host "Using PYTHONPATH=$env:PYTHONPATH"
Write-Host "Starting backend on http://127.0.0.1:$Port ..."

& $VenvPython -m uvicorn app.main:app --host 127.0.0.1 --port $Port
