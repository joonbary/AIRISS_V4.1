@echo off
:: Safe rollback script for AIRISS v4.1
:: English only, no special characters

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo ================================================================
echo AIRISS v4.1 - Safe Rollback to Original Database
echo ================================================================
echo.

echo Checking for backup file...
if exist "app\db\database_backup.py" (
    echo SUCCESS: Backup file found
) else (
    echo ERROR: No backup file found (database_backup.py)
    echo Cannot rollback without backup
    pause
    exit /b 1
)

echo.
echo Current database status:
python -c "import sys, os; sys.path.insert(0, os.getcwd()); exec(open('test_db_simple.py').read())" 2>nul

echo.
set /p confirm="Do you want to rollback to original database.py? (y/N): "
if /i not "%confirm%"=="y" (
    echo Rollback cancelled
    pause
    exit /b 0
)

echo.
echo Creating safety backup of current version...
copy "app\db\database.py" "app\db\database_enhanced_backup.py" > nul
echo SUCCESS: Current version saved as database_enhanced_backup.py

echo.
echo Restoring original database.py...
copy "app\db\database_backup.py" "app\db\database.py" > nul
echo SUCCESS: Original database.py restored

echo.
echo Testing restored configuration...
python -c "import sys, os; sys.path.insert(0, os.getcwd()); exec(open('test_db_simple.py').read())" 2>nul

echo.
echo ================================================================
echo Rollback completed successfully!
echo ================================================================
echo.
echo Original database.py has been restored
echo Enhanced version saved as: database_enhanced_backup.py
echo.
echo To re-apply enhanced version later:
echo copy "app\db\database_enhanced_backup.py" "app\db\database.py"
echo.
pause
