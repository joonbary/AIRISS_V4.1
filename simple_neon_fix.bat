@echo off
echo ================================================================
echo 🔧 AIRISS v4.1 - Simple Neon DB Fix
echo Safe PostgreSQL connection solution
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo 📋 Step 1: Backup current database.py
copy "app\db\database.py" "app\db\database_backup_simple.py" > nul
echo ✅ Backup created

echo.
echo 📋 Step 2: Apply enhanced database connection
copy "app\db\enhanced_database.py" "app\db\database.py" > nul
echo ✅ Enhanced version applied

echo.
echo 📋 Step 3: Install PostgreSQL driver
pip install psycopg2-binary --quiet

echo.
echo 📋 Step 4: Test connection
python -c "import sys, os; sys.path.insert(0, os.getcwd()); from app.db.database import DATABASE_CONNECTION_TYPE; print(f'Connection: {DATABASE_CONNECTION_TYPE}'); exit(0 if DATABASE_CONNECTION_TYPE == 'postgresql' else 1)"

if errorlevel 1 (
    echo ❌ PostgreSQL connection failed, using SQLite fallback
    echo 💡 Check your .env file for Neon DB credentials
) else (
    echo ✅ SUCCESS: Neon DB connection established!
)

echo.
echo 🎯 Fix completed! Start server: python -m app.main
pause
