@echo off
:: AIRISS v4.1 - Safe Neon DB Connection Fix (English Only)
:: No special characters or emojis to avoid encoding issues

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo ================================================================
echo AIRISS v4.1 - Neon DB Connection Fix (Safe Mode)
echo ================================================================
echo.

echo Step 1: Backup current database.py
if exist "app\db\database.py" (
    copy "app\db\database.py" "app\db\database_backup.py" > nul
    echo SUCCESS: Backup created as database_backup.py
) else (
    echo ERROR: Original database.py not found
    pause
    exit /b 1
)

echo.
echo Step 2: Apply enhanced database connection
if exist "app\db\enhanced_database.py" (
    copy "app\db\enhanced_database.py" "app\db\database.py" > nul
    echo SUCCESS: Enhanced database.py applied
) else (
    echo ERROR: Enhanced database.py not found
    echo Restoring backup...
    copy "app\db\database_backup.py" "app\db\database.py" > nul
    pause
    exit /b 1
)

echo.
echo Step 3: Testing new database connection
python -c "import sys, os; sys.path.insert(0, os.getcwd()); exec(open('test_db_simple.py').read())"

echo.
echo ================================================================
echo Fix completed successfully!
echo ================================================================
echo.
echo Next steps:
echo 1. Start AIRISS: python -m app.main
echo 2. Check health: http://localhost:8002/health
echo 3. Verify database type in dashboard
echo.
echo To rollback if needed:
echo copy "app\db\database_backup.py" "app\db\database.py"
echo.
pause
