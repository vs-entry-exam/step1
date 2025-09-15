param(
  [switch]$Backend,
  [switch]$Frontend,
  [switch]$All
)

$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir  # step1 directory

function Start-Backend {
  Write-Host "Starting backend (FastAPI)..." -ForegroundColor Cyan
  Set-Location "$Root/apps/api"
  if (Test-Path ".venv/Scripts/Activate.ps1") {
    . .venv/Scripts/Activate.ps1
  }
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}

function Start-Frontend {
  Write-Host "Starting frontend (Next.js)..." -ForegroundColor Green
  Set-Location "$Root/apps/web"
  npm run dev -p 3000
}

if ($All) {
  # Launch two consoles in parallel
  $backendCmd = "& { Set-Location '$Root/apps/api'; if (Test-Path '.venv/Scripts/Activate.ps1') { . .venv/Scripts/Activate.ps1 }; uvicorn main:app --host 0.0.0.0 --port 8000 --reload }"
  $frontendCmd = "& { Set-Location '$Root/apps/web'; npm run dev -p 3000 }"
  Start-Process pwsh -ArgumentList '-NoExit','-Command',$backendCmd | Out-Null
  Start-Process pwsh -ArgumentList '-NoExit','-Command',$frontendCmd | Out-Null
  Write-Host "Launched backend and frontend in separate terminals." -ForegroundColor Yellow
  exit 0
}

if ($Backend) { Start-Backend; exit 0 }
if ($Frontend) { Start-Frontend; exit 0 }

Write-Host "Usage: pwsh -File scripts/dev.ps1 -Backend | -Frontend | -All" -ForegroundColor Yellow
exit 1

