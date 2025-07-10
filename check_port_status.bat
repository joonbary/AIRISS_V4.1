@echo off
chcp 65001 > nul
echo 🔍 AIRISS 포트 상태 확인 도구
echo ===========================

echo.
echo 📊 주요 포트 사용 현황:
echo.

echo 🔸 포트 8002 (AIRISS 기본):
netstat -ano | findstr :8002
if errorlevel 1 (
    echo   ✅ 사용 가능
) else (
    echo   ❌ 사용 중
)

echo.
echo 🔸 포트 8003 (대체 1):
netstat -ano | findstr :8003
if errorlevel 1 (
    echo   ✅ 사용 가능
) else (
    echo   ❌ 사용 중
)

echo.
echo 🔸 포트 8004 (대체 2):
netstat -ano | findstr :8004
if errorlevel 1 (
    echo   ✅ 사용 가능
) else (
    echo   ❌ 사용 중
)

echo.
echo 🔸 포트 8005 (대체 3):
netstat -ano | findstr :8005
if errorlevel 1 (
    echo   ✅ 사용 가능
) else (
    echo   ❌ 사용 중
)

echo.
echo 🐍 Python 프로세스:
tasklist | findstr /i python.exe | findstr /v /i "Windows\System32"

echo.
echo 💡 포트 해결 옵션:
echo   1. solve_port_conflict.bat  - 포트 8002 충돌 해결
echo   2. run_port_8003.bat       - 포트 8003으로 실행
echo   3. run_alternative_port.bat - 자동 포트 선택

echo.
pause
