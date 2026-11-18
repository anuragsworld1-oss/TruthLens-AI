<#
.SYNOPSIS
  TruthLens AI - Windows one-click local launcher.
.DESCRIPTION
  Starts the Flask backend (http://127.0.0.1:5000) and the Vite React
  frontend (http://localhost:3000) in separate windows. Creates the Python
  virtual environment and installs frontend dependencies on first run.
.NOTES
  If script execution is blocked, run once:
    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#>

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Definition

function Write-Step($msg) { Write-Host "[TruthLens] $msg" -ForegroundColor Cyan }

# --- 1. Python virtual environment ---
$Venv = Join-Path $Root ".venv"
$VenvPython = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Step "Creating Python virtual environment (.venv)..."
    python -m venv $Venv
    Write-Step "Installing backend Python dependencies..."
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r (Join-Path $Root "backend\requirements.txt")
} else {
    Write-Step "Python virtual environment found."
}

# --- 2. Frontend dependencies ---
$NodeModules = Join-Path $Root "frontend\node_modules"
if (-not (Test-Path $NodeModules)) {
    Write-Step "Installing frontend npm dependencies (this may take a minute)..."
    Push-Location (Join-Path $Root "frontend")
    npm install
    Pop-Location
} else {
    Write-Step "Frontend node_modules found."
}

# --- 3. Launch backend in a new window ---
Write-Step "Starting Flask backend on http://127.0.0.1:5000 ..."
$BackendCmd = "`$env:PYTHONPATH='$Root\backend;$Root\ml_pipeline'; & '$VenvPython' '$Root\backend\run.py'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendCmd

# --- 4. Launch frontend in a new window ---
Start-Sleep -Seconds 2
Write-Step "Starting Vite frontend on http://localhost:3000 ..."
$FrontendCmd = "Set-Location '$Root\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCmd

Write-Host ""
Write-Host "[TruthLens] Both servers are launching in separate windows." -ForegroundColor Green
Write-Host "  Backend  : http://127.0.0.1:5000/api/health" -ForegroundColor Yellow
Write-Host "  Frontend : http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Close the two pop-up windows to stop the servers." -ForegroundColor Gray
