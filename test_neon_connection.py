#!/usr/bin/env python3
"""
AIRISS v4.1 - Neon DB Connection Test and Verification
Comprehensive testing of database connections and functionality
"""

import os
import sys
from pathlib import Path
import traceback

# Add project root to path
current_file = Path(__file__).resolve()
project_root = current_file.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("=" * 70)
print("🧪 AIRISS v4.1 - Neon DB Connection Test & Verification")
print("=" * 70)

def test_environment():
    """Test environment variables"""
    print("\n1. 🔧 Environment Variables Test:")
    
    required_vars = {
        "DATABASE_TYPE": os.getenv("DATABASE_TYPE"),
        "POSTGRES_DATABASE_URL": os.getenv("POSTGRES_DATABASE_URL"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
    }
    
    all_good = True
    for var, value in required_vars.items():
        if value:
            if "postgresql" in str(value):
                print(f"   ✅ {var}: PostgreSQL URL (configured)")
            else:
                print(f"   📝 {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
            if var in ["POSTGRES_DATABASE_URL", "DATABASE_URL"]:
                all_good = False
    
    return all_good

def test_dependencies():
    """Test required dependencies"""
    print("\n2. 📦 Dependencies Test:")
    
    dependencies = {
        "sqlalchemy": "Database ORM",
        "psycopg2": "PostgreSQL driver", 
        "python-dotenv": "Environment variables"
    }
    
    all_good = True
    for dep, desc in dependencies.items():
        try:
            module = __import__(dep.replace("-", "_"))
            version = getattr(module, '__version__', 'Available')
            print(f"   ✅ {dep}: {version} ({desc})")
        except ImportError:
            print(f"   ❌ {dep}: Not installed ({desc})")
            if dep == "psycopg2":
                all_good = False
    
    return all_good

def test_direct_neon_connection():
    """Test direct connection to Neon DB"""
    print("\n3. 🐘 Direct Neon DB Connection Test:")
    
    postgres_url = os.getenv("POSTGRES_DATABASE_URL") or os.getenv("DATABASE_URL")
    
    if not postgres_url:
        print("   ❌ No PostgreSQL URL found")
        return False
    
    if not postgres_url.startswith("postgresql"):
        print("   ❌ Invalid PostgreSQL URL format")
        return False
    
    try:
        import psycopg2
        
        print("   🔗 Attempting direct connection to Neon DB...")
        
        # Test connection
        conn = psycopg2.connect(
            postgres_url,
            sslmode='require',
            connect_timeout=30
        )
        
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        # Test table creation (if needed)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                test_data VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Test insert
        cursor.execute(
            "INSERT INTO connection_test (test_data) VALUES (%s) RETURNING id;",
            ("AIRISS Connection Test",)
        )
        test_id = cursor.fetchone()[0]
        
        # Test select
        cursor.execute("SELECT test_data FROM connection_test WHERE id = %s;", (test_id,))
        test_result = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"   ✅ Direct connection successful!")
        print(f"   📄 PostgreSQL Version: {version[0] if version else 'Unknown'}")
        print(f"   🧪 Test record created with ID: {test_id}")
        print(f"   📊 Test data retrieved: {test_result[0] if test_result else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Direct connection failed: {e}")
        
        error_msg = str(e).lower()
        if "timeout" in error_msg:
            print("   💡 Solution: Check network connectivity or Neon DB status")
        elif "authentication" in error_msg or "password" in error_msg:
            print("   💡 Solution: Verify credentials in .env file")
        elif "ssl" in error_msg:
            print("   💡 Solution: SSL configuration issue")
        elif "host" in error_msg:
            print("   💡 Solution: Check Neon DB host address")
        
        return False

def test_enhanced_database_module():
    """Test the enhanced database module"""
    print("\n4. 🔧 Enhanced Database Module Test:")
    
    try:
        # Test if we're using the enhanced module
        from app.db.database import (
            get_database_info, 
            test_connection, 
            DATABASE_CONNECTION_TYPE,
            force_postgresql_connection
        )
        
        print("   ✅ Enhanced database module loaded")
        
        # Get database info
        db_info = get_database_info()
        
        print(f"   📊 Connection Type: {DATABASE_CONNECTION_TYPE}")
        print(f"   🔗 Connected: {db_info.get('is_connected', False)}")
        print(f"   🚗 Driver: {db_info.get('engine_info', {}).get('driver', 'Unknown')}")
        print(f"   🏠 Host: {db_info.get('engine_info', {}).get('host', 'Unknown')}")
        print(f"   🎯 Priority: {db_info.get('connection_priority', 'Unknown')}")
        
        # Test connection
        connection_result = test_connection()
        print(f"   🧪 Connection Test: {'✅ Success' if connection_result else '❌ Failed'}")
        
        # If not PostgreSQL, try to force it
        if DATABASE_CONNECTION_TYPE != "postgresql":
            print("   🔧 Attempting to force PostgreSQL connection...")
            force_result = force_postgresql_connection()
            if force_result["success"]:
                print("   🎉 Force PostgreSQL: Success!")
                return True
            else:
                print(f"   ❌ Force PostgreSQL failed: {force_result['error']}")
        
        return DATABASE_CONNECTION_TYPE == "postgresql"
        
    except Exception as e:
        print(f"   ❌ Enhanced database module test failed: {e}")
        print(f"   📝 Error details: {traceback.format_exc()}")
        return False

def test_application_startup():
    """Test if the application can start with new database"""
    print("\n5. 🚀 Application Startup Test:")
    
    try:
        from app.main import app, DATABASE_ENABLED
        
        print("   ✅ Application module loaded successfully")
        print(f"   🗄️ Database Enabled: {DATABASE_ENABLED}")
        
        # Test health endpoint simulation
        try:
            from app.db.database import get_database_info
            db_info = get_database_info()
            
            health_status = {
                "status": "healthy",
                "database": {
                    "enabled": DATABASE_ENABLED,
                    "connected": db_info.get("is_connected", False),
                    "type": db_info.get("type", "unknown")
                }
            }
            
            print(f"   🏥 Health Check: {health_status['status']}")
            print(f"   📊 DB Status: {health_status['database']}")
            
            return True
            
        except Exception as e:
            print(f"   ⚠️ Health check simulation failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Application startup test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("\n" + "=" * 70)
    print("🧪 Running Comprehensive Test Suite")
    print("=" * 70)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Dependencies", test_dependencies), 
        ("Direct Neon Connection", test_direct_neon_connection),
        ("Enhanced Database Module", test_enhanced_database_module),
        ("Application Startup", test_application_startup),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your AIRISS system is ready with Neon DB connection")
        print("🚀 You can now start your server with cloud database")
    elif results.get("Direct Neon Connection", False):
        print("\n⚠️ PARTIAL SUCCESS")
        print("✅ Neon DB connection works")
        print("🔧 Some integration issues may need attention")
    else:
        print("\n❌ TESTS FAILED")
        print("💡 Check your .env file and Neon DB configuration")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        
        print("\n" + "=" * 70)
        print("🔧 Next Steps:")
        
        if success:
            print("1. ✅ Start AIRISS: python -m app.main")
            print("2. ✅ Check health: http://localhost:8002/health")
            print("3. ✅ Verify cloud storage in dashboard")
        else:
            print("1. 🔧 Fix .env configuration")
            print("2. 🔧 Run: pip install psycopg2-binary")
            print("3. 🔧 Check Neon DB accessibility")
            print("4. 🔧 Re-run this test")
        
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        print(f"📝 Error details: {traceback.format_exc()}")
