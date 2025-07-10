@echo off
chcp 65001 > nul
echo 🎯 AIRISS v4.1 포트 설정 및 실행 스크립트
echo =========================================

echo.
echo 📍 현재 포트 사용 현황 확인
echo 기본 포트 8002 상태:
netstat -ano | findstr :8002

echo.
echo 포트 8003 상태:
netstat -ano | findstr :8003

echo.
echo 포트 8004 상태:
netstat -ano | findstr :8004

echo.
echo 📍 사용 가능한 포트로 AIRISS 실행
echo 포트 8003을 사용합니다...

echo.
echo 🚀 AIRISS v4.1을 포트 8003에서 시작합니다...
echo 🌐 접속 주소: http://localhost:8003
echo.

set SERVER_PORT=8003
python -m app.main

echo.
echo ✅ AIRISS 실행 완료!
pause
