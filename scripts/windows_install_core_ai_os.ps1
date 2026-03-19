<# Standalone Windows installer for Core AI OS stack #>
Param()

Write-Host "[Install] Core AI OS – Windows Installer" -ForegroundColor Cyan

# 1) Ensure Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "[Install] Installing Python via winget..." -ForegroundColor Yellow
    winget install -e --id Python.Python.3.11 -h
  } else {
    Write-Host "[Install] Python not found and winget not available. Please install Python 3.11+ manually." -ForegroundColor Red
    exit 1
  }
}

Write-Host "[Install] Creating virtual environment..." -ForegroundColor Cyan
$venvPath = ".\venv"
if (-not (Test-Path $venvPath)) {
  python -m venv $venvPath
}
& (Join-Path $venvPath "Scripts\pip.exe") install -r requirements.txt

Write-Host "[Install] Installing npm dependencies if present..." -ForegroundColor Cyan
if (Test-Path ./package.json) {
  npm install
} elseif (Test-Path ./frontend/package.json) {
  (cd frontend; npm install)
}

Write-Host "[Install] Starting backend and kernel in background..." -ForegroundColor Cyan
Start-Process -FilePath "$venvPath\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000" -WindowStyle Hidden
Start-Process -FilePath "$venvPath\Scripts\python.exe" -ArgumentList "-m", "core.kernel_runtime", "--config", "config/god_ai_config.yaml" -WindowStyle Hidden

Write-Host "[Install] All services started in background." -ForegroundColor Green
