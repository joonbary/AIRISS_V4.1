@echo off
chcp 65001 > nul
echo ================================================================
echo 🔄 AIRISS v4.1 - Safety Rollback Script
echo Restore original database configuration if needed
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo 📋 Available backup files:
dir "app\db\database_backup_*.py" 2>nul
if errorlevel 1 (
    echo ❌ No backup files found!
    echo 💡 Your original database.py might not have been backed up
    pause
    exit /b 1
)

echo.
echo 🔍 Current database status:
python -c "
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from app.db.database import DATABASE_CONNECTION_TYPE, get_database_info
    db_info = get_database_info()
    print(f'Current connection: {DATABASE_CONNECTION_TYPE}')
    print(f'Connected: {db_info[\"is_connected\"]}')
    print(f'Driver: {db_info[\"engine_info\"][\"driver\"]}')
except Exception as e:
    print(f'Error checking current status: {e}')
"

echo.
set /p confirm="🤔 Do you want to rollback to original database.py? (y/N): "
if /i not "%confirm%"=="y" (
    echo ❌ Rollback cancelled
    pause
    exit /b 0
)

echo.
echo 📋 Finding most recent backup...
for /f "delims=" %%i in ('dir /b /o:-d "app\db\database_backup_*.py" 2^>nul') do (
    set "latest_backup=%%i"
    goto :found_backup
)

:found_backup
if not defined latest_backup (
    echo ❌ No backup file found!
    pause
    exit /b 1
)

echo ✅ Latest backup found: %latest_backup%

echo.
echo 📋 Creating safety backup of current database.py
copy "app\db\database.py" "app\db\database_enhanced_backup.py" > nul
echo ✅ Current version backed up as: database_enhanced_backup.py

echo.
echo 📋 Restoring original database.py
copy "app\db\%latest_backup%" "app\db\database.py" > nul
echo ✅ Original database.py restored from: %latest_backup%

echo.
echo 📋 Testing restored configuration
python -c "
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    # Force reload of the module
    if 'app.db.database' in sys.modules:
        del sys.modules['app.db.database']
    
    from app.db.database import get_database_info, test_connection
    
    db_info = get_database_info()
    print(f'Restored connection type: {db_info[\"type\"]}')
    print(f'Connected: {db_info[\"is_connected\"]}')
    print(f'Driver: {db_info[\"engine_info\"][\"driver\"]}')
    
    if db_info['is_connected']:
        print('✅ Restored configuration working correctly')
    else:
        print('⚠️ Restored configuration has connection issues')
        
except Exception as e:
    print(f'❌ Error testing restored configuration: {e}')
"

echo.
echo ================================================================
echo 🎯 Rollback Status Summary
echo ================================================================
echo.
echo ✅ Original database.py has been restored
echo 📁 Enhanced version saved as: database_enhanced_backup.py
echo 📁 Backup used: %latest_backup%
echo.
echo 🔧 To re-apply enhanced version later:
echo    copy "app\db\database_enhanced_backup.py" "app\db\database.py"
echo.
echo 🚀 You can now restart AIRISS with original configuration
echo.
pause
