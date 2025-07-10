@echo off
chcp 65001 > nul
echo 🔧 AIRISS v4.1 포트 충돌 해결 스크립트
echo ========================================

echo.
echo 📍 1단계: 포트 8002 사용 프로세스 확인
netstat -ano | findstr :8002
echo.

echo 📍 2단계: AIRISS 관련 프로세스 확인
tasklist | findstr python.exe
echo.

echo 📍 3단계: 포트 8002 사용 프로세스 종료
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo 프로세스 ID %%a를 종료합니다...
    taskkill /PID %%a /F 2>nul
)

echo.
echo 📍 4단계: 잠시 대기 후 포트 확인
timeout /t 3 /nobreak > nul
netstat -ano | findstr :8002

echo.
echo 📍 5단계: AIRISS 서버 재시작
echo python -m app.main을 실행하세요.

echo.
echo ✅ 포트 충돌 해결 완료!
pause
