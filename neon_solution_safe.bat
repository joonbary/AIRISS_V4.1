@echo off
:: AIRISS v4.1 - Main Neon DB Solution (Safe Mode)
:: English only, no special characters or emojis

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo ================================================================
echo AIRISS v4.1 - Neon DB Connection Solution
echo ================================================================
echo.

echo Current environment check:
python -c "import os; print('DATABASE_TYPE:', os.getenv('DATABASE_TYPE', 'Not Set')); print('POSTGRES_URL:', 'SET' if os.getenv('POSTGRES_DATABASE_URL') else 'NOT SET')"

echo.
echo Available options:
echo.
echo 1. FIX - Apply enhanced Neon DB connection
echo 2. TEST - Test current database connection only  
echo 3. ROLLBACK - Restore original database.py
echo 4. EXIT - Exit without changes
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto :fix
if "%choice%"=="2" goto :test
if "%choice%"=="3" goto :rollback
if "%choice%"=="4" goto :exit
echo Invalid choice, please try again
goto :start

:fix
echo.
echo Starting automatic fix...
call "fix_neon_safe.bat"
goto :end

:test
echo.
echo Running database connection test...
python "test_db_simple.py"
goto :end

:rollback
echo.
echo Starting rollback...
call "rollback_safe.bat"
goto :end

:exit
echo.
echo Exiting without changes
goto :end

:end
echo.
echo ================================================================
echo Operation completed
echo ================================================================
echo.
echo Available files:
echo - fix_neon_safe.bat (apply enhanced connection)
echo - test_db_simple.py (test connection)
echo - rollback_safe.bat (restore original)
echo.
pause

:start
goto :choice
