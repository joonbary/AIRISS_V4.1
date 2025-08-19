@echo off
echo ========================================
echo   AIRISS v5.0 서버 실행 스크립트
echo ========================================
echo.

REM Django 서버 실행 (포트 8000)
echo [1/2] Django 서버 시작 (포트 8000)...
start /B cmd /c "python manage.py runserver 8000 2>nul"
timeout /t 2 /nobreak >nul

REM FastAPI 서버 실행 (포트 8001)
echo [2/2] FastAPI 서버 시작 (포트 8001)...
cd app
start /B cmd /c "uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
cd ..
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   ✅ 서버 실행 완료!
echo ========================================
echo.
echo Django: http://localhost:8000/airiss/
echo FastAPI: http://localhost:8001/docs
echo.
echo 브라우저 열기...
start "" "http://localhost:8000/airiss/"

echo.
echo 종료하려면 아무 키나 누르세요...
pause >nul

REM 서버 종료
taskkill /F /IM python.exe 2>nul
echo 서버가 종료되었습니다.