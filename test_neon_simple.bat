@echo off
echo ================================================================
echo AIRISS v4.1 - Simple Neon DB Test (English Only)
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo Testing Neon DB connection...
python test_neon_connection.py

echo.
echo Test completed. Check results above.
echo.
pause
