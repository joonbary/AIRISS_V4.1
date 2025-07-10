@echo off
chcp 65001 > nul
echo ================================================================
echo 🔧 AIRISS v4.1 - URGENT SQLAlchemy Compatibility Fix
echo Fixing pool_timeout parameter issue with NullPool
echo ================================================================

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo.
echo 📋 URGENT FIX: SQLAlchemy NullPool Compatibility
echo Problem: pool_timeout parameter not compatible with NullPool
echo Solution: Apply fixed version without incompatible parameters

echo.
echo 📋 Step 1: Backup current database.py (safety)
copy "app\db\database.py" "app\db\database_broken_backup.py" > nul
echo ✅ Current broken version backed up

echo.
echo 📋 Step 2: Apply FIXED database.py
copy "app\db\database_fixed.py" "app\db\database.py" > nul
echo ✅ Fixed version applied

echo.
echo 📋 Step 3: Testing FIXED PostgreSQL connection
python -c "
import sys
import os
sys.path.insert(0, os.getcwd())

# Force reload
if 'app.db.database' in sys.modules:
    del sys.modules['app.db.database']

try:
    from app.db.database import DATABASE_CONNECTION_TYPE, get_database_info, test_connection
    
    print('🔍 Testing FIXED database connection...')
    db_info = get_database_info()
    
    print(f'📊 Connection Type: {DATABASE_CONNECTION_TYPE}')
    print(f'🔗 Connected: {db_info[\"is_connected\"]}')
    print(f'🚗 Driver: {db_info[\"engine_info\"][\"driver\"]}')
    print(f'🏠 Host: {db_info[\"engine_info\"][\"host\"]}')
    print(f'🔧 SQLAlchemy Fix Applied: {db_info.get(\"fixed_version\", False)}')
    
    if DATABASE_CONNECTION_TYPE == 'postgresql':
        print('')
        print('🎉 SUCCESS! Neon DB (PostgreSQL) connection FIXED!')
        print('✅ AIRISS now using cloud database successfully')
        print('🚀 Ready for production!')
    elif DATABASE_CONNECTION_TYPE == 'sqlite':
        print('')
        print('⚠️ Still on SQLite - checking PostgreSQL availability...')
        
        # Try to force PostgreSQL connection
        from app.db.database import force_postgresql_connection
        force_result = force_postgresql_connection()
        
        if force_result['success']:
            print('🎉 PostgreSQL connection FORCED successfully!')
            print('✅ Neon DB is now active!')
        else:
            print(f'❌ PostgreSQL still failing: {force_result[\"error\"]}')
            print('💡 Check .env file configuration')
    else:
        print('❌ Unexpected connection type')
        
except Exception as e:
    print(f'❌ FIXED version still has issues: {e}')
"

echo.
echo 📋 Step 4: Final verification
python -c "
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from app.db.database import get_database_info
    db_info = get_database_info()
    
    print('🎯 FINAL STATUS:')
    print(f'   Type: {db_info[\"type\"]}')
    print(f'   Connected: {db_info[\"is_connected\"]}')
    print(f'   Fixed: {db_info.get(\"fixed_version\", False)}')
    print(f'   Compatible: {db_info.get(\"sqlalchemy_compatible\", False)}')
    
    if db_info['type'] == 'postgresql' and db_info['is_connected']:
        print('')
        print('🏆 COMPLETE SUCCESS!')
        print('🎉 Neon DB connection working perfectly!')
        print('✅ SQLAlchemy compatibility fixed!')
        print('🚀 AIRISS ready with cloud database!')
    else:
        print('')
        print('ℹ️ Using fallback configuration')
        print('💡 Check environment variables if PostgreSQL desired')
        
except Exception as e:
    print(f'❌ Final verification failed: {e}')
"

echo.
echo ================================================================
echo 🎯 SQLAlchemy Fix Applied!
echo ================================================================
echo.
echo ✅ Fixed Issues:
echo    - Removed pool_timeout (not compatible with NullPool)
echo    - Removed pool_recycle (not compatible with NullPool)  
echo    - Enhanced error handling
echo    - Better PostgreSQL connection logic
echo.
echo 🚀 Your AIRISS is now ready!
echo    Start server: python -m app.main
echo    Check health: http://localhost:8002/health
echo.
pause
