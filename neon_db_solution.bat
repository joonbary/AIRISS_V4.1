@echo off
chcp 65001 > nul
echo ================================================================
echo 🎯 AIRISS v4.1 - Complete Neon DB Connection Solution
echo Step-by-step guide to fix SQLite to PostgreSQL connection
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo 📋 Quick Status Check:
python -c "
import os
print(f'DATABASE_TYPE: {os.getenv(\"DATABASE_TYPE\", \"Not Set\")}')
postgres_url = os.getenv('POSTGRES_DATABASE_URL', '')
if postgres_url:
    print('POSTGRES_DATABASE_URL: ✅ Configured')
else:
    print('POSTGRES_DATABASE_URL: ❌ Not Set')
"

echo.
echo ================================================================
echo 🚀 SOLUTION MENU - Choose your approach:
echo ================================================================
echo.
echo 1. 🔧 AUTOMATIC FIX (Recommended)
echo    - Backup current database.py
echo    - Apply enhanced connection logic
echo    - Test Neon DB connection
echo    - Rollback if failed
echo.
echo 2. 🧪 TEST ONLY (Diagnosis)
echo    - Test current Neon DB connectivity
echo    - Check all dependencies
echo    - No changes to code
echo.
echo 3. 🔄 ROLLBACK (If needed)
echo    - Restore original database.py
echo    - Undo any previous changes
echo.
echo 4. ❌ EXIT
echo.

set /p choice="👉 Enter your choice (1-4): "

if "%choice%"=="1" goto :automatic_fix
if "%choice%"=="2" goto :test_only
if "%choice%"=="3" goto :rollback
if "%choice%"=="4" goto :exit
goto :invalid_choice

:automatic_fix
echo.
echo ================================================================
echo 🔧 AUTOMATIC FIX - Enhanced Neon DB Connection
echo ================================================================
echo.
echo 📋 This will:
echo    1. Backup your current database.py
echo    2. Apply enhanced PostgreSQL connection logic
echo    3. Test the connection automatically
echo    4. Rollback if anything fails
echo.
set /p confirm="🤔 Proceed with automatic fix? (y/N): "
if /i not "%confirm%"=="y" goto :menu

echo.
echo 🚀 Starting automatic fix...
call "fix_neon_db_connection.bat"

echo.
echo 📊 Running post-fix verification...
python "test_neon_connection.py"

echo.
echo ✅ Automatic fix completed!
goto :end

:test_only
echo.
echo ================================================================
echo 🧪 TEST ONLY - Diagnosis and Connectivity Check
echo ================================================================
echo.
echo 📋 This will test:
echo    1. Environment variables
echo    2. Dependencies (psycopg2, etc.)
echo    3. Direct Neon DB connection
echo    4. Current database module
echo    5. Application compatibility
echo.
echo 🔍 Running comprehensive tests...
python "test_neon_connection.py"

echo.
echo 📊 Test completed! Check results above.
goto :end

:rollback
echo.
echo ================================================================
echo 🔄 ROLLBACK - Restore Original Configuration
echo ================================================================
echo.
echo ⚠️ WARNING: This will restore your original database.py
echo    Any enhanced features will be removed
echo.
set /p confirm="🤔 Are you sure you want to rollback? (y/N): "
if /i not "%confirm%"=="y" goto :menu

echo.
echo 🔄 Starting rollback...
call "rollback_database.bat"

echo.
echo ✅ Rollback completed!
goto :end

:invalid_choice
echo.
echo ❌ Invalid choice. Please enter 1, 2, 3, or 4.
timeout /t 2 > nul
goto :menu

:menu
echo.
goto :choice

:exit
echo.
echo 👋 Exiting without changes.
goto :end

:end
echo.
echo ================================================================
echo 📚 TROUBLESHOOTING GUIDE
echo ================================================================
echo.
echo ❌ If Neon DB connection fails:
echo    1. Check your .env file for correct POSTGRES_DATABASE_URL
echo    2. Verify Neon DB is accessible: https://console.neon.tech
echo    3. Install PostgreSQL driver: pip install psycopg2-binary
echo    4. Check network/firewall settings
echo.
echo ✅ If everything works:
echo    1. Start AIRISS: python -m app.main
echo    2. Check health: http://localhost:8002/health
echo    3. Verify database type in dashboard
echo.
echo 🔄 If you need to switch back:
echo    1. Run this script again
echo    2. Choose option 3 (Rollback)
echo.
echo 📞 Support files created:
echo    - enhanced_database.py (improved connection logic)
echo    - test_neon_connection.py (comprehensive testing)
echo    - fix_neon_db_connection.bat (automatic fix)
echo    - rollback_database.bat (safety rollback)
echo.
pause
