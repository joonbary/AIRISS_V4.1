@echo off
chcp 65001 >nul
echo ============================================
echo 🚀 AIRISS v4.1 안전한 빠른 시작
echo ============================================
echo.

echo [1] 가상환경 활성화 중...
call venv_new\Scripts\activate
if errorlevel 1 (
    echo ❌ 가상환경 활성화 실패
    pause
    exit /b 1
)

echo [2] 사용 가능한 포트 찾는 중...
echo    - 포트 8003 확인 중...
netstat -ano | findstr :8003 >nul
if errorlevel 1 (
    echo ✅ 포트 8003 사용 가능!
    echo [3] AIRISS 서버 시작 중 (포트 8003)...
    echo.
    echo 🌐 브라우저에서 열어주세요:
    echo    👉 http://localhost:8003/
    echo    👉 http://localhost:8003/health (상태 확인)
    echo    👉 http://localhost:8003/docs (API 문서)
    echo.
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
    goto :end
)

echo    - 포트 8004 확인 중...
netstat -ano | findstr :8004 >nul
if errorlevel 1 (
    echo ✅ 포트 8004 사용 가능!
    echo [3] AIRISS 서버 시작 중 (포트 8004)...
    echo.
    echo 🌐 브라우저에서 열어주세요:
    echo    👉 http://localhost:8004/
    echo    👉 http://localhost:8004/health (상태 확인)
    echo    👉 http://localhost:8004/docs (API 문서)
    echo.
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
    goto :end
)

echo    - 포트 8005 확인 중...
netstat -ano | findstr :8005 >nul
if errorlevel 1 (
    echo ✅ 포트 8005 사용 가능!
    echo [3] AIRISS 서버 시작 중 (포트 8005)...
    echo.
    echo 🌐 브라우저에서 열어주세요:
    echo    👉 http://localhost:8005/
    echo    👉 http://localhost:8005/health (상태 확인)
    echo    👉 http://localhost:8005/docs (API 문서)
    echo.
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
    goto :end
)

echo ❌ 포트 8003, 8004, 8005 모두 사용 중입니다.
echo 💡 수동으로 다른 포트를 시도해보세요:
echo    python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
echo    python -m uvicorn app.main:app --host 0.0.0.0 --port 9000

:end
echo.
echo ============================================
echo 서버를 중지하려면 Ctrl+C를 누르세요
echo ============================================
pause
