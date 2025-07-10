# PowerShell에서 AIRISS v5.0 즉시 실행
Write-Host "===============================================" -ForegroundColor Green
Write-Host "AIRISS v5.0 PowerShell 즉시 실행" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green

# 인코딩 설정
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = (Get-Location).Path
$env:LANG = "ko_KR.UTF-8"

Write-Host "인코딩 설정: UTF-8" -ForegroundColor Yellow
Write-Host "현재 위치: $((Get-Location).Path)" -ForegroundColor Cyan
Write-Host ""

# .env 파일 확인
if (-not (Test-Path ".env")) {
    Write-Host ".env 파일 생성 중..." -ForegroundColor Yellow
    if (Test-Path ".env.template") {
        Copy-Item ".env.template" ".env"
        Write-Host ".env 파일 생성 완료" -ForegroundColor Green
    }
}

Write-Host "AIRISS v5.0 시작 중..." -ForegroundColor Green
Write-Host "접속: http://localhost:8002" -ForegroundColor Yellow
Write-Host "종료: Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# AIRISS 실행
try {
    & uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
}
catch {
    Write-Host "uvicorn 직접 실행 실패. Python 모듈 방식 시도..." -ForegroundColor Red
    try {
        & python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
    }
    catch {
        Write-Host "Python 직접 실행 방식 시도..." -ForegroundColor Red
        & python -c "import sys; sys.path.insert(0, '.'); from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8002)"
    }
}
