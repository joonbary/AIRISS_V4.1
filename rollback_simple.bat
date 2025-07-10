@echo off
echo ================================================================
echo AIRISS v4.1 - Emergency Rollback (English Only)
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo Looking for backup files...
dir "app\db\database_backup_*.py"

echo.
set /p confirm="Rollback to original database.py? (y/N): "
if /i not "%confirm%"=="y" (
    echo Rollback cancelled
    pause
    exit /b 0
)

echo.
for /f "delims=" %%i in ('dir /b /o:-d "app\db\database_backup_*.py" 2^>nul') do (
    set "latest_backup=%%i"
    goto :found
)

:found
if defined latest_backup (
    copy "app\db\%latest_backup%" "app\db\database.py" > nul
    echo SUCCESS: Restored from %latest_backup%
) else (
    echo ERROR: No backup found
)

echo.
pause
