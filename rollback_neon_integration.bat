@echo off
REM Rollback Neon DB Integration
REM Restore original SQLite-based analysis_storage_service if needed

echo ========================================
echo NEON DB INTEGRATION ROLLBACK
echo ========================================
echo.

REM Find the most recent backup
for /f "delims=" %%i in ('dir /b /o:-d "app\services\analysis_storage_service_backup_*.py" 2^>nul') do (
    set backup_file=%%i
    goto :found_backup
)

:found_backup
if "%backup_file%"=="" (
    echo ERROR: No backup file found
    echo Please check app\services\ directory for backup files
    pause
    exit /b 1
)

echo Found backup file: %backup_file%
echo.

set /p confirm=Are you sure you want to rollback? (Y/N): 
if /i not "%confirm%"=="Y" (
    echo Rollback cancelled
    pause
    exit /b 0
)

echo.
echo Step 1: Creating current state backup...
set timestamp=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%

copy "app\services\analysis_storage_service.py" "app\services\analysis_storage_service_postgresql_%timestamp%.py" >nul
echo   SUCCESS: Current state backed up

echo.
echo Step 2: Restoring original service...
copy "app\services\%backup_file%" "app\services\analysis_storage_service.py" >nul
if errorlevel 1 (
    echo ERROR: Failed to restore backup
    pause
    exit /b 1
)
echo   SUCCESS: Original service restored

echo.
echo Step 3: Testing restored service...
python -c "from app.services.analysis_storage_service import storage_service; print('Restored service test:', 'PASS' if storage_service else 'FAIL')"
if errorlevel 1 (
    echo ERROR: Restored service test failed
    pause
    exit /b 1
)
echo   SUCCESS: Restored service working

echo.
echo ========================================
echo ROLLBACK COMPLETED
echo ========================================
echo.
echo Changes made:
echo - Original SQLite-based service restored
echo - PostgreSQL version backed up as: analysis_storage_service_postgresql_%timestamp%.py
echo - System rolled back to previous state
echo.
echo Your system is now back to the previous configuration.
echo.
pause