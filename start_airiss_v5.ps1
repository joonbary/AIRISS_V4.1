# PowerShell 실행 정책 설정 (필요시)
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Write-Host "===============================================" -ForegroundColor Green
Write-Host "AIRISS v5.0 - PowerShell 인코딩 안전 버전" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# 인코딩 설정
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = (Get-Location).Path
$env:LANG = "ko_KR.UTF-8"

Write-Host "인코딩 설정 완료..." -ForegroundColor Yellow
Write-Host "현재 디렉토리: $((Get-Location).Path)" -ForegroundColor Cyan
Write-Host "Python 경로: $env:PYTHONPATH" -ForegroundColor Cyan
Write-Host "인코딩: $env:PYTHONIOENCODING" -ForegroundColor Cyan
Write-Host ""

# Python 버전 확인
Write-Host "Python 버전 확인:" -ForegroundColor Yellow
python --version

# .env 파일 확인
if (-not (Test-Path ".env")) {
    Write-Host ".env 파일이 없습니다. 생성 중..." -ForegroundColor Yellow
    if (Test-Path ".env.template") {
        Copy-Item ".env.template" ".env"
        Write-Host ".env 파일 생성 완료" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "AIRISS v5.0 시작 중..." -ForegroundColor Green
Write-Host "접속 주소: http://localhost:8002" -ForegroundColor Yellow
Write-Host "종료: Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# AIRISS 실행
try {
    uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
}
catch {
    Write-Host "uvicorn 실행 실패. Python 모듈 방식으로 재시도..." -ForegroundColor Red
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
}
