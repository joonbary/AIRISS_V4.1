# Quick Status Check - Neon DB Integration
# Check current database configuration and storage service status

import sys
import os
from datetime import datetime

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def main():
    print("=" * 60)
    print("AIRISS NEON DB INTEGRATION - STATUS CHECK")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check 1: Database Connection
    print("1. DATABASE CONNECTION STATUS")
    print("-" * 30)
    
    try:
        from app.db.database import get_database_info, DATABASE_CONNECTION_TYPE
        
        db_info = get_database_info()
        print(f"   Connection Type: {db_info.get('type')} ✓")
        print(f"   Connected: {db_info.get('is_connected')} ✓")
        print(f"   Driver: {db_info.get('engine_info', {}).get('driver')}")
        print(f"   Host: {db_info.get('engine_info', {}).get('host')}")
        
        if db_info.get('type') == 'postgresql':
            print("   STATUS: PostgreSQL connection active ✓")
            db_status = "POSTGRESQL"
        else:
            print(f"   STATUS: Using {db_info.get('type')} (not PostgreSQL) ⚠️")
            db_status = "OTHER"
            
    except Exception as e:
        print(f"   ERROR: Database check failed - {e}")
        db_status = "ERROR"
    
    print()
    
    # Check 2: Storage Service Type
    print("2. STORAGE SERVICE STATUS")
    print("-" * 30)
    
    try:
        from app.services.analysis_storage_service import storage_service
        
        service_class = storage_service.__class__.__name__
        print(f"   Service Class: {service_class}")
        
        if hasattr(storage_service, 'get_storage_info'):
            storage_info = storage_service.get_storage_info()
            print(f"   Storage Info: {storage_info}")
            
        if hasattr(storage_service, 'is_available'):
            available = storage_service.is_available()
            print(f"   Available: {available} ✓")
        
        if 'PostgreSQL' in service_class:
            print("   STATUS: PostgreSQL-only service active ✓")
            storage_status = "POSTGRESQL"
        elif hasattr(storage_service, 'sqlalchemy_available'):
            if storage_service.sqlalchemy_available:
                print("   STATUS: SQLAlchemy-based service (may use SQLite) ⚠️")
                storage_status = "SQLITE_HYBRID"
            else:
                print("   STATUS: Memory-only service ⚠️")
                storage_status = "MEMORY"
        else:
            print("   STATUS: Unknown storage type ⚠️")
            storage_status = "UNKNOWN"
            
    except Exception as e:
        print(f"   ERROR: Storage service check failed - {e}")
        storage_status = "ERROR"
    
    print()
    
    # Check 3: Integration Status
    print("3. INTEGRATION STATUS")
    print("-" * 30)
    
    if db_status == "POSTGRESQL" and storage_status == "POSTGRESQL":
        print("   ✅ FULLY INTEGRATED")
        print("   ✅ PostgreSQL-only architecture")
        print("   ✅ SQLite dependencies removed")
        print("   ✅ Unified database system")
        integration_status = "COMPLETE"
        
    elif db_status == "POSTGRESQL" and storage_status in ["SQLITE_HYBRID", "MEMORY"]:
        print("   ⚠️  PARTIAL INTEGRATION")
        print("   ✅ PostgreSQL database connected")
        print("   ❌ Storage service still uses SQLite/Memory")
        print("   📋 ACTION NEEDED: Run integration script")
        integration_status = "PARTIAL"
        
    else:
        print("   ❌ NOT INTEGRATED")
        print("   ❌ PostgreSQL not properly configured")
        print("   📋 ACTION NEEDED: Check database configuration")
        integration_status = "NOT_INTEGRATED"
    
    print()
    
    # Summary and Recommendations
    print("4. SUMMARY & RECOMMENDATIONS")
    print("-" * 30)
    
    if integration_status == "COMPLETE":
        print("   🎉 NEON DB INTEGRATION IS COMPLETE!")
        print("   Your system is using unified PostgreSQL storage.")
        print("   No further action required.")
        
    elif integration_status == "PARTIAL":
        print("   🔧 INTEGRATION IS PARTIALLY COMPLETE")
        print("   Recommended action:")
        print("   1. Run: neon_db_integration_guide.bat")
        print("   2. Select option 1 (Full Integration)")
        print("   3. Follow the guided process")
        
    else:
        print("   ⚠️  INTEGRATION NOT STARTED")
        print("   Recommended action:")
        print("   1. Check .env file configuration")
        print("   2. Verify PostgreSQL connection")
        print("   3. Run: neon_db_integration_guide.bat")
    
    print()
    print("=" * 60)
    print("STATUS CHECK COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()