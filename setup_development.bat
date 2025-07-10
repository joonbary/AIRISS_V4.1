@echo off
echo ===============================================
echo AIRISS v5.0 - Development Environment Setup
echo ===============================================
echo.

echo Step 1: Switch to clean branch
echo ===============================================
git checkout v5-clean-final
git pull origin v5-clean-final
echo Updated to latest clean branch

echo.
echo Step 2: Create .env file from template
echo ===============================================
if not exist .env (
    copy .env.template .env
    echo .env file created from template
    echo.
    echo IMPORTANT: Please edit .env file with your actual API keys
    echo 1. Open .env in notepad
    echo 2. Replace 'your-openai-api-key-here' with your actual OpenAI API key
    echo 3. Save the file
    echo.
    notepad .env
) else (
    echo .env file already exists
)

echo.
echo Step 3: Check Python environment
echo ===============================================
python --version
echo.

echo Step 4: Install dependencies
echo ===============================================
pip install -r requirements.txt
echo Dependencies installed

echo.
echo Step 5: Test the application
echo ===============================================
echo Starting AIRISS v5.0...
echo Press Ctrl+C to stop the application
echo.
echo If everything works correctly, you should see:
echo "AIRISS v5.0 Server is running on port 8002"
echo.
python main.py

echo.
echo ===============================================
echo SETUP COMPLETED!
echo ===============================================
echo Your AIRISS v5.0 is ready to use!
echo Access: http://localhost:8002
echo.
pause
