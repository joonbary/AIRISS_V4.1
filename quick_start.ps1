Write-Host "AIRISS v5.0 Starting..." -ForegroundColor Green
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = (Get-Location).Path
$env:LANG = "ko_KR.UTF-8"

Write-Host "Encoding: UTF-8" -ForegroundColor Yellow
Write-Host "Path: $((Get-Location).Path)" -ForegroundColor Cyan
Write-Host "Access: http://localhost:8002" -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.template") {
        Copy-Item ".env.template" ".env"
        Write-Host ".env file created" -ForegroundColor Green
    }
}

try {
    uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
}
catch {
    Write-Host "Trying alternative method..." -ForegroundColor Red
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
}
