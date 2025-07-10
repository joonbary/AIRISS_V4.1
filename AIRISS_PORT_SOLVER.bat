@echo off
chcp 65001 > nul
title AIRISS v4.1 - 포트 충돌 종합 해결사
color 0A

echo.
echo ╔══════════════════════════════════════════╗
echo ║      🎯 AIRISS v4.1 포트 충돌 해결사     ║
echo ║                                          ║
echo ║  포트 충돌 문제를 자동으로 해결합니다    ║
echo ╚══════════════════════════════════════════╝
echo.

echo 📊 현재 상황 진단 중...
echo.

REM 포트 8002 상태 확인
netstat -ano | findstr :8002 > nul
if errorlevel 1 (
    echo ✅ 포트 8002: 사용 가능
    goto :run_default
) else (
    echo ❌ 포트 8002: 사용 중
)

echo.
echo 🔧 해결 방법을 선택하세요:
echo.
echo 1. 포트 8002 충돌 해결 후 실행
echo 2. 포트 8003으로 실행
echo 3. 자동 포트 선택 (Python 도구)
echo 4. 포트 상태만 확인
echo 5. 종료
echo.

set /p CHOICE="선택 (1-5): "

if "%CHOICE%"=="1" goto :fix_port_8002
if "%CHOICE%"=="2" goto :use_port_8003
if "%CHOICE%"=="3" goto :use_python_tool
if "%CHOICE%"=="4" goto :check_status_only
if "%CHOICE%"=="5" goto :end
goto :invalid_choice

:fix_port_8002
echo.
echo 🔧 포트 8002 충돌 해결 중...
call solve_port_conflict.bat
goto :end

:use_port_8003
echo.
echo 🚀 포트 8003으로 실행...
call run_port_8003.bat
goto :end

:use_python_tool
echo.
echo 🐍 Python 포트 관리 도구 실행...
python port_manager.py
goto :end

:check_status_only
echo.
echo 📊 포트 상태 확인...
call check_port_status.bat
goto :end

:run_default
echo.
echo ✅ 포트 8002가 사용 가능합니다!
echo.
set /p RUN_NOW="지금 AIRISS를 시작하시겠습니까? (Y/n): "
if /i "%RUN_NOW%"=="n" goto :end

echo.
echo 🚀 AIRISS v4.1 시작 중...
echo 🌐 접속 주소: http://localhost:8002
echo.
python -m app.main
goto :end

:invalid_choice
echo.
echo ❌ 잘못된 선택입니다. 1-5 중에서 선택하세요.
timeout /t 2 /nobreak > nul
goto :menu

:end
echo.
echo 💡 추가 도움말:
echo    - 문제가 지속되면 시스템 재시작을 시도하세요
echo    - 방화벽이나 백신 프로그램이 포트를 차단할 수 있습니다
echo    - 관리자 권한으로 실행하면 더 많은 권한을 얻을 수 있습니다
echo.
pause
