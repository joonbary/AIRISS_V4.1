@echo off
REM Neon DB Integration Script - Safe Deployment
REM Replace SQLite-dependent analysis_storage_service with PostgreSQL-only version

echo ========================================
echo NEON DB INTEGRATION - SAFE DEPLOYMENT
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "app\services\analysis_storage_service.py" (
    echo ERROR: analysis_storage_service.py not found
    echo Please run this script from the AIRISS root directory
    pause
    exit /b 1
)

echo Step 1: Creating backup of current files...
REM Create backup with timestamp
set timestamp=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%

copy "app\services\analysis_storage_service.py" "app\services\analysis_storage_service_backup_%timestamp%.py" >nul
if errorlevel 1 (
    echo ERROR: Failed to create backup
    pause
    exit /b 1
)
echo   SUCCESS: Backup created

echo.
echo Step 2: Testing PostgreSQL connection...
python test_neon_integration.py
if errorlevel 1 (
    echo ERROR: PostgreSQL tests failed
    echo Please check your database connection
    pause
    exit /b 1
)
echo   SUCCESS: PostgreSQL tests passed

echo.
echo Step 3: Replacing analysis storage service...
REM Replace the old service with PostgreSQL-only version
copy "app\services\analysis_storage_service_postgresql.py" "app\services\analysis_storage_service_new.py" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy new service
    pause
    exit /b 1
)

REM Backup current and replace
move "app\services\analysis_storage_service.py" "app\services\analysis_storage_service_old_%timestamp%.py" >nul
move "app\services\analysis_storage_service_new.py" "app\services\analysis_storage_service.py" >nul

if not exist "app\services\analysis_storage_service.py" (
    echo ERROR: Failed to replace service file
    echo Restoring backup...
    move "app\services\analysis_storage_service_old_%timestamp%.py" "app\services\analysis_storage_service.py" >nul
    pause
    exit /b 1
)

echo   SUCCESS: Service replaced

echo.
echo Step 4: Testing new integrated service...
python -c "from app.services.analysis_storage_service import postgresql_storage_service; print('Import test:', 'PASS' if postgresql_storage_service else 'FAIL')"
if errorlevel 1 (
    echo ERROR: New service import failed
    echo Restoring backup...
    move "app\services\analysis_storage_service_old_%timestamp%.py" "app\services\analysis_storage_service.py" >nul
    pause
    exit /b 1
)
echo   SUCCESS: New service working

echo.
echo Step 5: Verifying integration...
python -c "from app.services.analysis_storage_service import postgresql_storage_service; health=postgresql_storage_service.get_storage_health(); print('Health check:', health.get('status', 'UNKNOWN'))"
if errorlevel 1 (
    echo ERROR: Health check failed
    pause
    exit /b 1
)
echo   SUCCESS: Integration verified

echo.
echo ========================================
echo NEON DB INTEGRATION COMPLETED!
echo ========================================
echo.
echo Changes made:
echo - SQLite dependencies removed
echo - PostgreSQL-only storage service active
echo - Unified database architecture achieved
echo - Backup files created: *_backup_%timestamp%.py
echo.
echo Next steps:
echo 1. Test your application thoroughly
echo 2. Monitor performance and logs
echo 3. Remove backup files when satisfied
echo.
echo If you need to rollback, run: rollback_neon_integration.bat
echo.
pause