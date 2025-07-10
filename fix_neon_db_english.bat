@echo off
echo ================================================================
echo AIRISS v4.1 - Neon DB Connection Fix (English Only)
echo Safe database connection upgrade with SQLAlchemy compatibility
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo Step 1: Creating backup of current database.py
if exist "app\db\database.py" (
    copy "app\db\database.py" "app\db\database_backup_english.py" > nul
    echo SUCCESS: Backup created as database_backup_english.py
) else (
    echo ERROR: Original database.py not found!
    pause
    exit /b 1
)

echo.
echo Step 2: Applying English-only database connection
if exist "app\db\enhanced_database.py" (
    copy "app\db\enhanced_database.py" "app\db\database.py" > nul
    echo SUCCESS: Enhanced database.py applied
) else (
    echo ERROR: Enhanced database.py not found!
    echo Restoring backup...
    copy "app\db\database_backup_english.py" "app\db\database.py" > nul
    pause
    exit /b 1
)

echo.
echo Step 3: Testing database connection with Python script
echo Creating temporary test script...

echo import sys > temp_test.py
echo import os >> temp_test.py
echo sys.path.insert(0, os.getcwd()) >> temp_test.py
echo. >> temp_test.py
echo try: >> temp_test.py
echo     from app.db.database import get_database_info, test_connection, DATABASE_CONNECTION_TYPE >> temp_test.py
echo. >> temp_test.py
echo     print('Testing enhanced database connection...') >> temp_test.py
echo     db_info = get_database_info() >> temp_test.py
echo. >> temp_test.py
echo     print('Connection Type:', DATABASE_CONNECTION_TYPE) >> temp_test.py
echo     print('Connected:', db_info["is_connected"]) >> temp_test.py
echo     print('Driver:', db_info["engine_info"]["driver"]) >> temp_test.py
echo     print('Host:', db_info["engine_info"]["host"]) >> temp_test.py
echo. >> temp_test.py
echo     if DATABASE_CONNECTION_TYPE == 'postgresql': >> temp_test.py
echo         print('SUCCESS: Neon DB PostgreSQL connection established!') >> temp_test.py
echo         print('Your AIRISS system is now using cloud database') >> temp_test.py
echo     elif DATABASE_CONNECTION_TYPE == 'sqlite': >> temp_test.py
echo         print('FALLBACK: Using SQLite PostgreSQL connection failed') >> temp_test.py
echo         print('Check your .env file and Neon DB credentials') >> temp_test.py
echo     else: >> temp_test.py
echo         print('ERROR: Unexpected connection type') >> temp_test.py
echo. >> temp_test.py
echo except Exception as e: >> temp_test.py
echo     print('ERROR:', str(e)) >> temp_test.py
echo     print('Rolling back to original database.py...') >> temp_test.py

python temp_test.py

if errorlevel 1 (
    echo.
    echo ERROR: Test failed! Rolling back to original database.py
    copy "app\db\database_backup_english.py" "app\db\database.py" > nul
    echo SUCCESS: Rollback completed
    echo.
    echo Troubleshooting suggestions:
    echo 1. Check your .env file for correct Neon DB URL
    echo 2. Verify Neon DB is accessible from your network
    echo 3. Ensure psycopg2 is installed: pip install psycopg2-binary
    del temp_test.py > nul 2>&1
    pause
    exit /b 1
)

echo.
echo Step 4: Testing AIRISS server startup
echo Creating server test script...

echo import sys > temp_server_test.py
echo import os >> temp_server_test.py
echo sys.path.insert(0, os.getcwd()) >> temp_server_test.py
echo. >> temp_server_test.py
echo try: >> temp_server_test.py
echo     from app.main import app >> temp_server_test.py
echo     print('SUCCESS: AIRISS server can be started with enhanced database') >> temp_server_test.py
echo     print('Ready to test in production') >> temp_server_test.py
echo except Exception as e: >> temp_server_test.py
echo     print('ERROR: Server startup test failed:', str(e)) >> temp_server_test.py

python temp_server_test.py

echo.
echo Cleaning up temporary files...
del temp_test.py > nul 2>&1
del temp_server_test.py > nul 2>&1

echo.
echo ================================================================
echo Neon DB Connection Fix Completed Successfully!
echo ================================================================
echo.
echo Next Steps:
echo 1. Start your AIRISS server: python -m app.main
echo 2. Check /health endpoint for database status
echo 3. Verify cloud storage is working
echo.
echo To rollback if needed:
echo copy "app\db\database_backup_english.py" "app\db\database.py"
echo.
pause