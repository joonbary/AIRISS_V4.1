@echo off
REM Neon DB Complete Integration Guide
REM Step-by-step guide for PostgreSQL unification

echo ========================================
echo NEON DB COMPLETE INTEGRATION GUIDE
echo ========================================
echo.
echo This guide will help you:
echo 1. Remove SQLite dependencies completely
echo 2. Unify all data storage to PostgreSQL (Neon DB)
echo 3. Test the integrated system
echo 4. Provide rollback options for safety
echo.

echo Current Status Check:
echo ----------------------

REM Check current database configuration
python -c "from app.db.database import get_database_info; info=get_database_info(); print('Database Type:', info.get('type')); print('Connected:', info.get('is_connected'))"

echo.
echo Available Options:
echo ==================
echo.
echo [1] Run Full Integration (Recommended)
echo     - Complete PostgreSQL unification
echo     - Remove SQLite dependencies
echo     - Includes safety backups
echo.
echo [2] Test Only (Safe)
echo     - Test new PostgreSQL service
echo     - No changes to current system
echo     - Verify integration readiness
echo.
echo [3] Rollback Previous Integration
echo     - Restore SQLite-based system
echo     - Use if integration caused issues
echo.
echo [4] System Status Check
echo     - Check current configuration
echo     - Database health verification
echo.
echo [5] Exit
echo.

set /p choice=Select option (1-5): 

if "%choice%"=="1" goto :full_integration
if "%choice%"=="2" goto :test_only
if "%choice%"=="3" goto :rollback
if "%choice%"=="4" goto :status_check
if "%choice%"=="5" goto :exit
goto :invalid_choice

:full_integration
echo.
echo FULL INTEGRATION SELECTED
echo =========================
echo.
echo This will:
echo - Backup current files
echo - Replace SQLite service with PostgreSQL-only version
echo - Test the integration
echo - Verify system health
echo.
set /p confirm=Continue with full integration? (Y/N): 
if /i not "%confirm%"=="Y" goto :exit

echo.
echo Starting full integration...
call integrate_neon_db.bat
goto :exit

:test_only
echo.
echo TEST ONLY SELECTED
echo ==================
echo.
echo Running integration tests without making changes...
python test_neon_integration.py
echo.
echo Test completed. Review results above.
echo If tests passed, you can run option 1 for full integration.
goto :main_menu

:rollback
echo.
echo ROLLBACK SELECTED
echo =================
echo.
echo This will restore the previous SQLite-based system.
call rollback_neon_integration.bat
goto :exit

:status_check
echo.
echo SYSTEM STATUS CHECK
echo ===================
echo.
echo Current Database Configuration:
python -c "from app.db.database import get_database_info; import json; print(json.dumps(get_database_info(), indent=2))"
echo.
echo Current Storage Service Info:
python -c "try: from app.services.analysis_storage_service import storage_service; print('Storage Service:', storage_service.__class__.__name__); print('Available:', storage_service.is_available() if hasattr(storage_service, 'is_available') else 'Unknown'); except Exception as e: print('Error:', e)"
echo.
goto :main_menu

:invalid_choice
echo.
echo Invalid choice. Please select 1-5.
goto :main_menu

:main_menu
echo.
echo ========================================
set /p return=Press Enter to return to main menu or type 'exit' to quit: 
if /i "%return%"=="exit" goto :exit
cls
goto :start

:exit
echo.
echo ========================================
echo NEON DB INTEGRATION GUIDE COMPLETED
echo ========================================
echo.
echo Documentation and support:
echo - Check logs for any error messages
echo - Backup files are preserved for safety
echo - Contact support if issues persist
echo.
pause
exit /b 0

:start
goto :main