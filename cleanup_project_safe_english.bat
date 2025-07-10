@echo off
chcp 65001 > nul
title AIRISS v4.1 Project Cleanup - Safe Version

echo ========================================
echo AIRISS v4.1 Project Cleanup
echo Safely removing redundant files
echo ========================================
echo.

echo WARNING: This will move redundant files to cleanup_backup folder
echo Press Ctrl+C to cancel, or any key to continue...
pause

echo.
echo [1/5] Creating backup directory...
mkdir "cleanup_backup\batch_files" 2>nul
mkdir "cleanup_backup\backup_files" 2>nul
mkdir "cleanup_backup\old_configs" 2>nul

echo.
echo [2/5] Moving redundant batch files...
move "deploy_*.bat" "cleanup_backup\batch_files\" 2>nul
move "fix_*.bat" "cleanup_backup\batch_files\" 2>nul
move "diagnose_*.bat" "cleanup_backup\batch_files\" 2>nul
move "emergency_*.bat" "cleanup_backup\batch_files\" 2>nul

echo.
echo [3/5] Moving backup configuration files...
move "*.backup" "cleanup_backup\backup_files\" 2>nul
move "requirements_*.txt" "cleanup_backup\backup_files\" 2>nul
move "Dockerfile.*" "cleanup_backup\backup_files\" 2>nul

echo.
echo [4/5] Moving old documentation...
move "*_GUIDE.md" "cleanup_backup\old_configs\" 2>nul
move "*_REPORT.md" "cleanup_backup\old_configs\" 2>nul
move "*_TROUBLESHOOTING.md" "cleanup_backup\old_configs\" 2>nul

echo.
echo [5/5] Keeping essential files...
echo Essential files kept:
echo - railway.json
echo - Dockerfile  
echo - requirements.txt
echo - app/
echo - airiss-v4-frontend/
echo - .env.example
echo - README.md

echo.
echo ========================================
echo CLEANUP COMPLETED!
echo ========================================
echo.
echo Cleaned project structure:
dir /B | findstr /V "cleanup_backup"

echo.
echo All moved files are safely stored in cleanup_backup/
echo You can restore them anytime if needed.
echo.
pause
