@echo off
echo ===============================================
echo AIRISS v4.0 - Frontend Restart
echo ===============================================
echo.

REM 기존 프로세스 종료
echo [1] Stopping existing frontend processes...
taskkill /F /IM node.exe 2>nul

REM 잠시 대기
timeout /t 2 /nobreak > nul

REM 프론트엔드 디렉토리로 이동
cd airiss-v4-frontend

REM 프론트엔드 시작
echo.
echo [2] Starting frontend server...
start cmd /k npm start

echo.
echo ===============================================
echo Frontend is starting on http://localhost:3000
echo Please wait for the browser to open...
echo ===============================================
pause