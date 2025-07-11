@echo off
chcp 65001 > nul
cls
echo 🎉 모든 Git Merge Conflict 해결 완료!
echo 🚀 AIRISS v4.1 서버 시작 (Excel 완전 개선 버전)
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📋 시스템 정보:
echo Python: 
python --version
echo 현재 경로: %CD%
echo.

echo 🔥 서버 시작...
echo 📊 Excel 다운로드 URL: http://localhost:8002/api/analysis-storage/export-excel
echo 📄 CSV 다운로드 URL:   http://localhost:8002/api/analysis-storage/export-csv
echo 🏥 헬스체크 URL:       http://localhost:8002/health
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

echo.
echo 서버가 종료되었습니다.
pause
