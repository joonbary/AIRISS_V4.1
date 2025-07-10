# AIRISS Python Fix - PowerShell Version
Write-Host "AIRISS Python 3.13 Fix Starting..." -ForegroundColor Green

Set-Location -Path $PSScriptRoot

# Clean old environment
if (Test-Path "venv_new") {
    Write-Host "Removing old venv_new..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv_new"
}

# Create new environment
Write-Host "Creating new virtual environment..." -ForegroundColor Cyan
python -m venv venv_new

# Activate environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "venv_new\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install packages
Write-Host "Installing packages..." -ForegroundColor Cyan
$packages = @(
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "python-multipart==0.0.6", 
    "jinja2==3.1.2",
    "aiosqlite==0.19.0",
    "pandas>=2.2.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "openpyxl==3.1.2",
    "aiofiles==23.2.1", 
    "python-dotenv==1.0.0",
    "pydantic>=2.5.0",
    "websockets==12.0"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor White
    pip install --only-binary=all $package
}

# Test imports
Write-Host "Testing package imports..." -ForegroundColor Cyan
try {
    python -c "import fastapi, uvicorn, pandas, numpy; print('SUCCESS: All packages working')"
    Write-Host "Package test passed!" -ForegroundColor Green
}
catch {
    Write-Host "Package test failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Start server
Write-Host "Starting AIRISS server on port 8003..." -ForegroundColor Green
Write-Host "URL: http://localhost:8003/" -ForegroundColor Yellow
Write-Host "Dashboard: http://localhost:8003/dashboard" -ForegroundColor Yellow

python -m uvicorn app.main:app --host 0.0.0.0 --port 8003

Read-Host "Press Enter to exit"
