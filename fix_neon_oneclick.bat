@echo off
:: AIRISS v4.1 - One-Click Neon DB Fix
:: Simplest possible solution

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo AIRISS v4.1 - One-Click Neon DB Fix
echo =====================================

echo 1. Creating backup...
if exist "app\db\database.py" (
    copy "app\db\database.py" "app\db\database_backup.py" > nul 2>&1
    echo   Backup created: database_backup.py
) else (
    echo   ERROR: database.py not found
    pause
    exit /b 1
)

echo.
echo 2. Applying fix...
if exist "app\db\enhanced_database.py" (
    copy "app\db\enhanced_database.py" "app\db\database.py" > nul 2>&1
    echo   Enhanced database applied
) else (
    echo   ERROR: enhanced_database.py not found
    copy "app\db\database_backup.py" "app\db\database.py" > nul 2>&1
    pause
    exit /b 1
)

echo.
echo 3. Testing connection...
python test_db_simple.py

echo.
echo =====================================
echo Fix completed! 
echo.
echo Start AIRISS: python -m app.main
echo Check health: http://localhost:8002/health
echo.
echo To rollback: copy "app\db\database_backup.py" "app\db\database.py"
echo.
pause
