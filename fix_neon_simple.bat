@echo off
echo ================================================================
echo AIRISS v4.1 - Neon DB Connection Fix (English Only)
echo Safe PostgreSQL connection setup
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo Step 1: Environment Check
python -c "import os; print('DATABASE_TYPE:', os.getenv('DATABASE_TYPE', 'Not Set')); print('POSTGRES_URL:', 'YES' if os.getenv('POSTGRES_DATABASE_URL') else 'NO')"

echo.
echo Step 2: Creating backup of current database.py
if exist "app\db\database.py" (
    copy "app\db\database.py" "app\db\database_backup_%date:~10,4%%date:~4,2%%date:~7,2%.py" > nul
    echo SUCCESS: Backup created
) else (
    echo ERROR: Original database.py not found
    pause
    exit /b 1
)

echo.
echo Step 3: Applying enhanced database connection
if exist "app\db\enhanced_database.py" (
    copy "app\db\enhanced_database.py" "app\db\database.py" > nul
    echo SUCCESS: Enhanced database.py applied
) else (
    echo ERROR: Enhanced database.py not found
    pause
    exit /b 1
)

echo.
echo Step 4: Testing connection
python -c "import sys, os; sys.path.insert(0, os.getcwd()); from app.db.database import get_database_info, DATABASE_CONNECTION_TYPE; info = get_database_info(); print('Connection Type:', DATABASE_CONNECTION_TYPE); print('Connected:', info['is_connected']); print('Driver:', info['engine_info']['driver'])"

echo.
echo ================================================================
echo Neon DB Connection Fix Completed
echo ================================================================
echo.
echo Next Steps:
echo 1. Start AIRISS: python -m app.main
echo 2. Check health: http://localhost:8002/health
echo 3. Verify cloud storage in dashboard
echo.
pause
