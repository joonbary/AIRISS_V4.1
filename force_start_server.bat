@echo off
chcp 65001 > nul
cls
echo 🚀 AIRISS 로컬 서버 강제 시작
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📋 포트 8002 상태 확인...
netstat -an | findstr ":8002"
if %errorlevel%==0 (
    echo ⚠️ 포트 8002가 이미 사용 중입니다. 프로세스를 종료합니다.
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8002"') do taskkill /f /pid %%a 2>nul
    timeout /t 2 /nobreak > nul
)

echo.
echo 🔥 새로운 Excel API와 함께 서버 시작...
echo 📊 Excel: http://localhost:8002/api/analysis-storage/export-excel
echo 📄 CSV:   http://localhost:8002/api/analysis-storage/export-csv
echo 🏥 Health: http://localhost:8002/health
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

pause
