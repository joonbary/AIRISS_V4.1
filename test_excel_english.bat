@echo off
REM AIRISS Excel Test - English Only

echo ========================================
echo AIRISS Excel Download Test - English Only
echo ========================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Running Excel download test...
echo.

python test_excel_download_english.py

echo.
echo Test completed!
pause
