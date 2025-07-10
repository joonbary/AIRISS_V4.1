@echo off
chcp 65001 > nul
echo ================================================================
echo AIRISS v4.1 - Environment Variables Fix
echo Ensure proper .env configuration - English only
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo Step 1: Checking .env file existence
if exist ".env" (
    echo SUCCESS: .env file found
) else (
    echo ERROR: .env file not found
    echo Creating .env file from template...
    
    if exist ".env.example" (
        copy ".env.example" ".env" > nul
        echo SUCCESS: .env created from .env.example
    ) else (
        echo ERROR: No .env.example found either
        pause
        exit /b 1
    )
)

echo.
echo Step 2: Reading current .env configuration
echo Current .env settings:
type .env | findstr /i "DATABASE_TYPE POSTGRES_DATABASE_URL DATABASE_URL"

echo.
echo Step 3: Testing environment variable loading
python -c "
import os
print('Before loading .env:')
print('DATABASE_TYPE:', os.getenv('DATABASE_TYPE', 'Not Set'))

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
    print('After loading .env:')
    print('DATABASE_TYPE:', os.getenv('DATABASE_TYPE', 'Not Set'))
    print('POSTGRES_DATABASE_URL:', 'SET' if os.getenv('POSTGRES_DATABASE_URL') else 'NOT SET')
    print('DATABASE_URL:', 'SET' if os.getenv('DATABASE_URL') else 'NOT SET')
    print('SUCCESS: Environment variables loaded correctly')
except Exception as e:
    print(f'ERROR loading environment variables: {e}')
"

echo.
echo Step 4: Ensuring DATABASE_TYPE is set to postgres
python -c "
import os
import re

# Read .env file
try:
    with open('.env', 'r') as f:
        content = f.read()
    
    # Check if DATABASE_TYPE is set to postgres
    if 'DATABASE_TYPE=postgres' in content:
        print('SUCCESS: DATABASE_TYPE already set to postgres')
    else:
        # Update or add DATABASE_TYPE=postgres
        if 'DATABASE_TYPE=' in content:
            content = re.sub(r'DATABASE_TYPE=.*', 'DATABASE_TYPE=postgres', content)
            print('UPDATED: Changed DATABASE_TYPE to postgres')
        else:
            content = 'DATABASE_TYPE=postgres\n' + content
            print('ADDED: DATABASE_TYPE=postgres to .env file')
        
        # Write back to .env
        with open('.env', 'w') as f:
            f.write(content)
        
        print('SUCCESS: .env file updated')
        
except Exception as e:
    print(f'ERROR updating .env file: {e}')
"

echo.
echo Step 5: Verifying PostgreSQL URL format
python -c "
import os
from dotenv import load_dotenv
load_dotenv(override=True)

postgres_url = os.getenv('POSTGRES_DATABASE_URL', '')
database_url = os.getenv('DATABASE_URL', '')

print('PostgreSQL URL validation:')

if postgres_url:
    if postgres_url.startswith('postgresql://'):
        print('POSTGRES_DATABASE_URL: VALID format')
        if '@ep-' in postgres_url and 'neon.tech' in postgres_url:
            print('POSTGRES_DATABASE_URL: Neon DB format detected')
        else:
            print('POSTGRES_DATABASE_URL: Custom PostgreSQL server')
    else:
        print('POSTGRES_DATABASE_URL: INVALID format (should start with postgresql://)')
else:
    print('POSTGRES_DATABASE_URL: NOT SET')

if database_url:
    if database_url.startswith('postgresql'):
        print('DATABASE_URL: VALID PostgreSQL format')
    else:
        print('DATABASE_URL: NOT PostgreSQL format')
else:
    print('DATABASE_URL: NOT SET')

# Check if at least one PostgreSQL URL is available
if postgres_url or (database_url and 'postgresql' in database_url):
    print('RESULT: PostgreSQL configuration AVAILABLE')
else:
    print('RESULT: PostgreSQL configuration MISSING')
    print('ACTION NEEDED: Add valid Neon DB URL to .env file')
"

echo.
echo ================================================================
echo Environment Variables Check Completed
================================================================
echo.
echo If PostgreSQL configuration is missing:
echo 1. Get your Neon DB connection string from: https://console.neon.tech
echo 2. Add it to .env file as: POSTGRES_DATABASE_URL=postgresql://...
echo 3. Ensure DATABASE_TYPE=postgres is set
echo.
echo Next step: Run apply_sqlalchemy_fix.bat
echo.
pause
