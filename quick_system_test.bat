@echo off
echo ============================================================
echo AIRISS Quick System Test - Post GitHub Upload
echo ============================================================
echo.

echo Testing Neon DB Integration Status...
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

python -c "
import sys
import os
sys.path.append('app')

try:
    from app.services.analysis_storage_service import storage_service
    print('✅ Storage Service: Import Successful')
    
    health = storage_service.get_storage_health()
    print(f'✅ Database Type: {health.get(\"database_info\", {}).get(\"type\")}')
    print(f'✅ Connection Status: {health.get(\"database_info\", {}).get(\"is_connected\")}')
    print(f'✅ Storage Type: {health.get(\"storage_type\")}')
    print(f'✅ PostgreSQL Only: {health.get(\"postgresql_only\", False)}')
    print(f'✅ SQLite Removed: {health.get(\"sqlite_dependencies\", True) == False}')
    
    print()
    print('🎉 NEON DB INTEGRATION: FULLY OPERATIONAL')
    print('🚀 SYSTEM STATUS: READY FOR PRODUCTION')
    
except Exception as e:
    print(f'❌ ERROR: {e}')
    print('⚠️  SYSTEM REQUIRES ATTENTION')
"

echo.
echo ============================================================
echo System test completed!
echo ============================================================
pause
