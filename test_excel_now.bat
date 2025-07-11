@echo off
chcp 65001 > nul
echo 🧪 AIRISS Excel Download Test
echo.

echo 📋 Starting AIRISS server and testing Excel download functionality...
echo.

REM Start server in background (if not already running)
echo 🚀 Starting local server...
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
timeout /t 5 /nobreak > nul

echo ⏳ Waiting for server to start...
timeout /t 3 /nobreak > nul

echo 🧪 Running Excel download test...
python test_excel_download.py

echo.
echo ✅ Test completed! Check the generated Excel and CSV files.
echo.
pause
