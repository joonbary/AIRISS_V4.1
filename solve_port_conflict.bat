@echo off
chcp 65001 > nul
echo 🔧 AIRISS v4.1 포트 충돌 완전 해결 가이드
echo =============================================

echo.
echo 📍 1단계: 현재 실행 중인 AIRISS 프로세스 확인
echo.
tasklist | findstr /i python
echo.

echo 📍 2단계: 포트 8002 사용 프로세스 상세 확인
echo.
for /f "tokens=1,2,3,4,5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo 프로토콜: %%a, 로컬주소: %%b, 외부주소: %%c, 상태: %%d, PID: %%e
    for /f "tokens=1" %%p in ('tasklist /fi "pid eq %%e" /fo csv /nh') do (
        echo   → 프로세스명: %%p
    )
)

echo.
echo 📍 3단계: 포트 8002 강제 해제
echo.
set /p CONFIRM="포트 8002를 사용하는 프로세스를 종료하시겠습니까? (Y/N): "
if /i "%CONFIRM%"=="Y" (
    echo 포트 8002 프로세스 종료 중...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
        echo 프로세스 ID %%a 종료 중...
        taskkill /PID %%a /F 2>nul
        if errorlevel 1 (
            echo   ❌ PID %%a 종료 실패
        ) else (
            echo   ✅ PID %%a 종료 성공
        )
    )
) else (
    echo 프로세스 종료를 건너뜁니다.
)

echo.
echo 📍 4단계: 포트 해제 확인
timeout /t 3 /nobreak > nul
echo 포트 8002 상태 재확인:
netstat -ano | findstr :8002
if errorlevel 1 (
    echo ✅ 포트 8002가 해제되었습니다!
) else (
    echo ⚠️ 포트 8002가 여전히 사용 중입니다.
)

echo.
echo 📍 5단계: AIRISS 서버 재시작
echo.
set /p RESTART="이제 AIRISS를 시작하시겠습니까? (Y/N): "
if /i "%RESTART%"=="Y" (
    echo.
    echo 🚀 AIRISS v4.1 시작 중...
    echo 🌐 접속 주소: http://localhost:8002
    echo.
    python -m app.main
) else (
    echo.
    echo 💡 수동으로 실행하려면:
    echo    python -m app.main
    echo.
    echo 💡 다른 포트로 실행하려면:
    echo    run_port_8003.bat
)

echo.
echo ✅ 포트 충돌 해결 과정 완료!
pause
