@echo off
chcp 65001 > nul
echo 🚀 AIRISS v4.1 대체 포트 실행 스크립트
echo =========================================

echo.
echo 📍 사용 가능한 대체 포트로 AIRISS 실행

set "available_ports=8003 8004 8005 8006 8007"

for %%p in (%available_ports%) do (
    echo.
    echo 🔍 포트 %%p 확인 중...
    netstat -ano | findstr :%%p > nul
    if errorlevel 1 (
        echo ✅ 포트 %%p 사용 가능!
        echo.
        echo 🚀 AIRISS v4.1을 포트 %%p에서 시작합니다...
        echo 🌐 접속 주소: http://localhost:%%p
        echo.
        set PORT=%%p
        python -m app.main
        goto :end
    ) else (
        echo ❌ 포트 %%p 사용 중
    )
)

echo.
echo ⚠️ 모든 대체 포트가 사용 중입니다.
echo 수동으로 포트를 지정하거나 fix_port_conflict.bat를 실행하세요.

:end
pause
