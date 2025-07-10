# AIRISS v4.1 Deployment Fix - PowerShell Version
# Encoding: UTF-8

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   AIRISS v4.1 Deployment Fix (PowerShell)"     -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check current Python
Write-Host "[Step 1] Current Python version:" -ForegroundColor Yellow
python --version
Write-Host ""

# Step 2: Backup existing venv
Write-Host "[Step 2] Backup existing virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    if (Test-Path "venv_backup") {
        Remove-Item "venv_backup" -Recurse -Force
    }
    Rename-Item "venv" "venv_backup"
    Write-Host "Backed up existing venv to venv_backup" -ForegroundColor Green
}

# Step 3: Check Python 3.11
Write-Host "[Step 3] Check Python 3.11..." -ForegroundColor Yellow
$python311 = py -3.11 --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python 3.11 not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.11.9 from python.org" -ForegroundColor Red
    Read-Host "Press Enter to continue after installation"
    exit 1
}
Write-Host "Python 3.11 found!" -ForegroundColor Green

# Step 4: Create new venv
Write-Host "[Step 4] Creating new virtual environment..." -ForegroundColor Yellow
py -3.11 -m venv venv_stable
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to create virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Virtual environment created!" -ForegroundColor Green

# Step 5: Activate venv
Write-Host "[Step 5] Activating virtual environment..." -ForegroundColor Yellow
& "venv_stable\Scripts\Activate.ps1"
Write-Host "Virtual environment activated!" -ForegroundColor Green

# Step 6: Upgrade pip
Write-Host "[Step 6] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Step 7: Install packages
Write-Host "[Step 7] Installing core packages..." -ForegroundColor Yellow
$packages = @(
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0", 
    "sqlalchemy==2.0.23",
    "pandas==2.1.3",
    "aiosqlite==0.19.0",
    "python-multipart==0.0.6",
    "jinja2==3.1.2",
    "aiofiles==23.2.1",
    "websockets==12.0"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Cyan
    pip install $package
}

# Install pydantic separately with binary-only
Write-Host "Installing pydantic (binary-only)..." -ForegroundColor Cyan
pip install "pydantic==2.5.0" --only-binary=all

# Step 8: Initialize database
Write-Host "[Step 8] Initializing database..." -ForegroundColor Yellow
python init_database.py

# Step 9: Test server
Write-Host "[Step 9] Testing server..." -ForegroundColor Yellow
Write-Host "Starting server for 5 seconds..." -ForegroundColor Cyan

$job = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & "venv_stable\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8002
}

Start-Sleep -Seconds 3
Start-Process "http://localhost:8002/health"

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "SUCCESS! AIRISS v4.1 Ready!" -ForegroundColor Green  
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Key URLs:" -ForegroundColor Yellow
Write-Host "- Main: http://localhost:8002/" -ForegroundColor White
Write-Host "- Health: http://localhost:8002/health" -ForegroundColor White
Write-Host "- Docs: http://localhost:8002/docs" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to continue"

# Stop the test server
Stop-Job $job -ErrorAction SilentlyContinue
Remove-Job $job -ErrorAction SilentlyContinue
