@echo off
echo ===============================================
echo AIRISS v5.0 - Clean Up Old Branches
echo ===============================================
echo.
echo This will delete the old problematic branches
echo WARNING: This cannot be undone!
echo.
set /p answer=Do you want to continue? (y/n): 
if /i "%answer%"=="y" goto :continue
if /i "%answer%"=="yes" goto :continue
goto :end

:continue
echo.
echo Step 1: Delete local branches
echo ===============================================
git branch -D airiss-v5-clean 2>nul
git branch -D main 2>nul
echo Local branches cleaned

echo.
echo Step 2: Delete remote branches
echo ===============================================
git push origin --delete airiss-v5-clean 2>nul
git push origin --delete main 2>nul
echo Remote branches cleaned

echo.
echo Step 3: Show remaining branches
echo ===============================================
git branch -a
echo.

echo ===============================================
echo CLEANUP COMPLETED!
echo ===============================================
echo Only clean branch remains: v5-clean-final
echo.

:end
pause
