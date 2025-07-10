@echo off
REM AIRISS v4.1 Quick Enhancement - Add missing optional modules
REM Encoding: ANSI

title AIRISS Quick Enhancement

echo ========================================
echo AIRISS v4.1 Quick Enhancement
echo Adding optional advanced features
echo ========================================

cd /d "%~dp0"

echo [1/3] Activating environment...
if exist venv_fixed\Scripts\activate.bat (
    call venv_fixed\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found
    pause
    exit /b 1
)

echo [2/3] Installing missing optional modules...
echo Installing SQLAlchemy for advanced search...
pip install sqlalchemy==2.0.23

echo Installing optional NLP packages...
pip install --only-binary=all transformers>=4.30.0 torch>=2.0.0

echo [3/3] Verification...
python -c "import sqlalchemy; print('✓ SQLAlchemy installed')"

echo.
echo ========================================
echo Enhancement Complete!
echo Restart AIRISS to use new features
echo ========================================
echo.
echo To restart: ultimate_fix.bat
echo.
pause
