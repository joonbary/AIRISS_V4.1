#!/usr/bin/env python3
"""
AIRISS v4.1 - Direct Neon DB Connection Test
Test PostgreSQL connection without SQLAlchemy complications
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("🧪 AIRISS v4.1 - Direct Neon DB Connection Test")
print("=" * 60)

def load_env_variables():
    """Load environment variables from .env file"""
    print("\n1. 📋 Loading Environment Variables:")
    
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        print(f"   📁 Found .env file: {env_file}")
        
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        
        print("   ✅ Environment variables loaded")
    else:
        print(f"   ❌ .env file not found: {env_file}")
        return False
    
    # Check key variables
    database_type = os.getenv("DATABASE_TYPE", "Not Set")
    postgres_url = os.getenv("POSTGRES_DATABASE_URL", "")
    database_url = os.getenv("DATABASE_URL", "")
    
    print(f"   📝 DATABASE_TYPE: {database_type}")
    print(f"   🐘 POSTGRES_DATABASE_URL: {'Set' if postgres_url else 'Not Set'}")
    print(f"   📄 DATABASE_URL: {'Set' if database_url else 'Not Set'}")
    
    return bool(postgres_url or database_url)

def test_psycopg2():
    """Test psycopg2 installation"""
    print("\n2. 📦 Testing psycopg2 (PostgreSQL Driver):")
    
    try:
        import psycopg2
        print(f"   ✅ psycopg2 version: {psycopg2.__version__}")
        return True
    except ImportError:
        print("   ❌ psycopg2 not installed")
        print("   💡 Install with: pip install psycopg2-binary")
        return False

def test_direct_connection():
    """Test direct PostgreSQL connection"""
    print("\n3. 🐘 Testing Direct Neon DB Connection:")
    
    # Get PostgreSQL URL
    postgres_url = os.getenv("POSTGRES_DATABASE_URL") or os.getenv("DATABASE_URL")
    
    if not postgres_url:
        print("   ❌ No PostgreSQL URL found")
        return False
    
    print(f"   🔗 URL: {postgres_url.split('@')[0]}@***")
    
    try:
        import psycopg2
        
        # Test connection
        print("   🔄 Connecting to Neon DB...")
        
        conn = psycopg2.connect(
            postgres_url,
            sslmode='require',
            connect_timeout=30
        )
        
        cursor = conn.cursor()
        
        # Test basic operations
        print("   🧪 Testing basic operations...")
        
        # 1. Version check
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"   📄 PostgreSQL Version: {version[0][:50]}...")
        
        # 2. Current time
        cursor.execute("SELECT NOW();")
        current_time = cursor.fetchone()
        print(f"   ⏰ Server Time: {current_time[0]}")
        
        # 3. Database name
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"   🗄️ Database: {db_name[0]}")
        
        # 4. Test table creation and operations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS airiss_connection_test (
                id SERIAL PRIMARY KEY,
                test_message VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Insert test data
        cursor.execute(
            "INSERT INTO airiss_connection_test (test_message) VALUES (%s) RETURNING id;",
            ("AIRISS v4.1 Connection Test Success",)
        )
        test_id = cursor.fetchone()[0]
        
        # Read back test data
        cursor.execute(
            "SELECT test_message, created_at FROM airiss_connection_test WHERE id = %s;",
            (test_id,)
        )
        test_result = cursor.fetchone()
        
        print(f"   ✅ Test Record ID: {test_id}")
        print(f"   📝 Test Message: {test_result[0]}")
        print(f"   📅 Created At: {test_result[1]}")
        
        # Cleanup
        cursor.execute("DELETE FROM airiss_connection_test WHERE id = %s;", (test_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("   🎉 Direct Neon DB connection: SUCCESS!")
        return True
        
    except Exception as e:
        print(f"   ❌ Direct connection failed: {e}")
        
        # Provide specific guidance based on error
        error_str = str(e).lower()
        if "timeout" in error_str:
            print("   💡 Network timeout - check your internet connection")
        elif "authentication" in error_str or "password" in error_str:
            print("   💡 Authentication failed - check credentials in .env")
        elif "ssl" in error_str:
            print("   💡 SSL issue - check sslmode requirement")
        elif "host" in error_str:
            print("   💡 Host unreachable - check Neon DB status")
        else:
            print("   💡 Check Neon DB console for connection details")
        
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection with fixed parameters"""
    print("\n4. ⚙️ Testing SQLAlchemy with Fixed Parameters:")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.pool import NullPool
        
        postgres_url = os.getenv("POSTGRES_DATABASE_URL") or os.getenv("DATABASE_URL")
        
        if not postgres_url:
            print("   ❌ No PostgreSQL URL found")
            return False
        
        print("   🔧 Creating SQLAlchemy engine with fixed parameters...")
        
        # Create engine with only compatible parameters
        engine = create_engine(
            postgres_url,
            poolclass=NullPool,
            echo=False,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 30,
            },
            pool_recycle=3600,
            # Removed pool_timeout - this was causing the error
        )
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            test_result = result.fetchone()
            
            if test_result and test_result[0] == 1:
                print("   ✅ SQLAlchemy connection: SUCCESS!")
                print("   🔧 Compatibility issues resolved")
                return True
            else:
                print("   ❌ SQLAlchemy test query failed")
                return False
                
    except Exception as e:
        print(f"   ❌ SQLAlchemy connection failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🏁 Running Comprehensive Test")
    print("=" * 60)
    
    tests = [
        ("Environment Variables", load_env_variables),
        ("psycopg2 Driver", test_psycopg2),
        ("Direct Neon DB Connection", test_direct_connection),
        ("SQLAlchemy Fixed Connection", test_sqlalchemy_connection),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if results.get("Direct Neon DB Connection", False):
        print("\n🎉 EXCELLENT! Neon DB connection is working!")
        print("✅ Your database credentials and network are fine")
        
        if results.get("SQLAlchemy Fixed Connection", False):
            print("✅ SQLAlchemy compatibility issues resolved")
            print("🚀 Ready to apply fix to AIRISS")
        else:
            print("⚠️ SQLAlchemy needs parameter adjustments")
    else:
        print("\n❌ Neon DB connection issues detected")
        print("🔧 Check credentials and network connectivity")
    
    return passed >= 3  # Need at least 3/4 to pass

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        
        print("\n" + "=" * 60)
        print("🎯 Recommendations:")
        
        if success:
            print("1. ✅ Run: quick_fix_neon.bat")
            print("2. ✅ Start AIRISS server")
            print("3. ✅ Check cloud database status")
        else:
            print("1. 🔧 Check .env file configuration")
            print("2. 🔧 Install: pip install psycopg2-binary")
            print("3. 🔧 Verify Neon DB in console")
            print("4. 🔧 Re-run this test")
        
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Test crashed: {e}")
