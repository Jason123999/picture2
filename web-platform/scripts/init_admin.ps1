$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$VenvPython = Join-Path $Root '.venv\Scripts\python.exe'

if (-not (Test-Path $VenvPython)) {
  throw "Python venv not found: $VenvPython"
}

$env:PYTHONPATH = $Backend
Set-Location $Backend

Write-Host "Using PYTHONPATH=$env:PYTHONPATH"
Write-Host "Running init_admin..."

& $VenvPython -u -m app.scripts.init_admin
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
