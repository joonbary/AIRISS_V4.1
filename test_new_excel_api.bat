@echo off
chcp 65001
echo ========================================
echo AIRISS New Excel API Test
echo ========================================
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo Testing new Excel/CSV endpoints...
echo.

python test_new_excel_api.py

echo.
echo ========================================
echo Test Complete!
echo ========================================
echo.
echo Check downloaded files in current directory
echo.
pause
