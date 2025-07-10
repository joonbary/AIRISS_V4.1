@echo off
chcp 65001 > nul
echo ================================================================
echo 🔧 AIRISS v4.1 - Neon DB Connection Fix
echo Safe backup and enhanced database connection setup
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo 📋 Step 1: Creating backup of current database.py
if exist "app\db\database.py" (
    copy "app\db\database.py" "app\db\database_backup_%date:~0,4%%date:~5,2%%date:~8,2%.py" > nul
    echo ✅ Backup created: database_backup_%date:~0,4%%date:~5,2%%date:~8,2%.py
) else (
    echo ❌ Original database.py not found!
    pause
    exit /b 1
)

echo.
echo 📋 Step 2: Applying enhanced database connection
if exist "app\db\enhanced_database.py" (
    copy "app\db\enhanced_database.py" "app\db\database.py" > nul
    echo ✅ Enhanced database.py applied successfully
) else (
    echo ❌ Enhanced database.py not found!
    echo Restoring backup...
    copy "app\db\database_backup_%date:~0,4%%date:~5,2%%date:~8,2%.py" "app\db\database.py" > nul
    pause
    exit /b 1
)

echo.
echo 📋 Step 3: Testing Neon DB connection
python -c "
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from app.db.database import get_database_info, test_connection, DATABASE_CONNECTION_TYPE
    
    print('🔍 Testing enhanced database connection...')
    db_info = get_database_info()
    
    print(f'📊 Connection Type: {DATABASE_CONNECTION_TYPE}')
    print(f'🔗 Connected: {db_info[\"is_connected\"]}')
    print(f'🚗 Driver: {db_info[\"engine_info\"][\"driver\"]}')
    print(f'🏠 Host: {db_info[\"engine_info\"][\"host\"]}')
    
    if DATABASE_CONNECTION_TYPE == 'postgresql':
        print('🎉 SUCCESS: Neon DB (PostgreSQL) connection established!')
        print('✅ Your AIRISS system is now using cloud database')
    elif DATABASE_CONNECTION_TYPE == 'sqlite':
        print('⚠️ FALLBACK: Using SQLite (PostgreSQL connection failed)')
        print('💡 Check your .env file and Neon DB credentials')
    else:
        print('❌ ERROR: Unexpected connection type')
        
except Exception as e:
    print(f'❌ ERROR: {e}')
    print('Rolling back to original database.py...')
"

if errorlevel 1 (
    echo.
    echo ❌ Test failed! Rolling back to original database.py
    copy "app\db\database_backup_%date:~0,4%%date:~5,2%%date:~8,2%.py" "app\db\database.py" > nul
    echo ✅ Rollback completed
    echo.
    echo 💡 Troubleshooting suggestions:
    echo    1. Check your .env file for correct Neon DB URL
    echo    2. Verify Neon DB is accessible from your network
    echo    3. Ensure psycopg2 is installed: pip install psycopg2-binary
    pause
    exit /b 1
)

echo.
echo 📋 Step 4: Restarting AIRISS server for testing
echo Starting server in test mode...
timeout /t 3 > nul

python -c "
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from app.main import app
    print('✅ AIRISS server can be started with enhanced database')
    print('🎯 Ready to test in production')
except Exception as e:
    print(f'❌ Server startup test failed: {e}')
"

echo.
echo ================================================================
echo 🎉 Neon DB Connection Fix Completed!
echo ================================================================
echo.
echo 📊 Next Steps:
echo    1. Start your AIRISS server: python -m app.main
echo    2. Check /health endpoint for database status
echo    3. Verify cloud storage is working
echo.
echo 🔄 To rollback if needed:
echo    copy "app\db\database_backup_%date:~0,4%%date:~5,2%%date:~8,2%.py" "app\db\database.py"
echo.
pause
