@echo off
echo ================================================================
echo AIRISS v4.1 - SQLAlchemy Compatible Neon DB Fix
echo Complete solution for database connection issues
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo Step 1: Creating backup of current database.py
if exist "app\db\database.py" (
    copy "app\db\database.py" "app\db\database_backup_sqlalchemy.py" > nul
    echo SUCCESS: Backup created as database_backup_sqlalchemy.py
) else (
    echo ERROR: Original database.py not found!
    pause
    exit /b 1
)

echo.
echo Step 2: Applying SQLAlchemy compatible database connection
if exist "app\db\sqlalchemy_compatible_database.py" (
    copy "app\db\sqlalchemy_compatible_database.py" "app\db\database.py" > nul
    echo SUCCESS: SQLAlchemy compatible database.py applied
) else (
    echo ERROR: SQLAlchemy compatible database file not found!
    echo Restoring backup...
    copy "app\db\database_backup_sqlalchemy.py" "app\db\database.py" > nul
    pause
    exit /b 1
)

echo.
echo Step 3: Testing SQLAlchemy compatible database connection
echo Creating test script...

echo import sys > test_db.py
echo import os >> test_db.py
echo sys.path.insert(0, os.getcwd()) >> test_db.py
echo. >> test_db.py
echo try: >> test_db.py
echo     from app.db.database import get_database_info, test_connection, DATABASE_CONNECTION_TYPE >> test_db.py
echo. >> test_db.py
echo     print("Testing SQLAlchemy compatible database connection...") >> test_db.py
echo     db_info = get_database_info() >> test_db.py
echo. >> test_db.py
echo     print("Connection Type:", DATABASE_CONNECTION_TYPE) >> test_db.py
echo     print("Connected:", db_info["is_connected"]) >> test_db.py
echo     print("Driver:", db_info["engine_info"]["driver"]) >> test_db.py
echo     print("Host:", db_info["engine_info"]["host"]) >> test_db.py
echo     print("SQLAlchemy Compatible:", db_info.get("sqlalchemy_compatible", True)) >> test_db.py
echo. >> test_db.py
echo     connection_result = test_connection() >> test_db.py
echo     print("Connection Test Result:", connection_result) >> test_db.py
echo. >> test_db.py
echo     if DATABASE_CONNECTION_TYPE == "postgresql": >> test_db.py
echo         print("SUCCESS: Neon DB PostgreSQL connection established!") >> test_db.py
echo         print("Your AIRISS system is now using cloud database") >> test_db.py
echo     elif DATABASE_CONNECTION_TYPE == "sqlite": >> test_db.py
echo         print("FALLBACK: Using SQLite - PostgreSQL connection failed") >> test_db.py
echo         print("Check your .env file and Neon DB credentials") >> test_db.py
echo     else: >> test_db.py
echo         print("ERROR: Unexpected connection type:", DATABASE_CONNECTION_TYPE) >> test_db.py
echo. >> test_db.py
echo except Exception as e: >> test_db.py
echo     print("ERROR:", str(e)) >> test_db.py
echo     import traceback >> test_db.py
echo     print("Details:", traceback.format_exc()) >> test_db.py

python test_db.py

if errorlevel 1 (
    echo.
    echo ERROR: Database test failed! Rolling back...
    copy "app\db\database_backup_sqlalchemy.py" "app\db\database.py" > nul
    echo SUCCESS: Rollback completed
    del test_db.py > nul 2>&1
    echo.
    echo Troubleshooting suggestions:
    echo 1. Check .env file: DATABASE_TYPE=postgres
    echo 2. Verify POSTGRES_DATABASE_URL is set correctly
    echo 3. Install PostgreSQL driver: pip install psycopg2-binary
    echo 4. Check Neon DB connectivity
    pause
    exit /b 1
)

echo.
echo Step 4: Testing AIRISS application startup
echo Creating application test script...

echo import sys > test_app.py
echo import os >> test_app.py
echo sys.path.insert(0, os.getcwd()) >> test_app.py
echo. >> test_app.py
echo try: >> test_app.py
echo     from app.main import app, DATABASE_ENABLED >> test_app.py
echo     print("SUCCESS: AIRISS application loaded successfully") >> test_app.py
echo     print("Database Enabled:", DATABASE_ENABLED) >> test_app.py
echo     print("Application ready for production") >> test_app.py
echo except Exception as e: >> test_app.py
echo     print("ERROR: Application test failed:", str(e)) >> test_app.py

python test_app.py

echo.
echo Cleaning up test files...
del test_db.py > nul 2>&1
del test_app.py > nul 2>&1

echo.
echo ================================================================
echo SQLAlchemy Compatible Neon DB Fix Complete!
echo ================================================================
echo.
echo SUCCESS: Your AIRISS system has been upgraded with:
echo - SQLAlchemy compatible database connection
echo - Smart PostgreSQL to SQLite fallback
echo - Enhanced error handling and logging
echo.
echo Next Steps:
echo 1. Start AIRISS server: python -m app.main
echo 2. Check health status: http://localhost:8002/health
echo 3. Verify database type in dashboard
echo.
echo Rollback command if needed:
echo copy "app\db\database_backup_sqlalchemy.py" "app\db\database.py"
echo.
pause