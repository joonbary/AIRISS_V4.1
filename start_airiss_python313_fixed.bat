@echo off
chcp 65001 > nul
echo.
echo ========================================
echo    AIRISS v4.1 Python 3.13 Safe Mode
echo ========================================
echo.
echo [Change Log]
echo   - Fixed SQLAlchemy Python 3.13 compatibility
echo   - Safe conditional database loading
echo   - All core analysis features work
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo [Current Directory]: %CD%
echo [Python Version]:
python --version
echo.

echo ========================================
echo  Core Features (Always Available):
echo    - File Upload
echo    - Text Analysis  
echo    - Quantitative Analysis
echo    - Hybrid Scoring
echo    - Bias Detection
echo.
echo  Optional Features (Python 3.13):
echo    - Database Storage (SQLAlchemy dependent)
echo    - Analysis History Management  
echo ========================================
echo.

echo [Starting AIRISS Server...]
echo [Browser]: Open http://localhost:8002
echo [Stop]: Press Ctrl+C
echo.

python app\main.py

pause
