#!/usr/bin/env python3
"""
AIRISS Database Connection Diagnosis Tool
Current database status checking and Neon DB connection troubleshooting
"""

import os
import sys
from pathlib import Path

# Add project root to path
current_file = Path(__file__).resolve()
project_root = current_file.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("=" * 60)
print("🔍 AIRISS Database Connection Diagnosis")
print("=" * 60)

# 1. Environment Variables Check
print("\n1. 📋 Environment Variables Check:")
env_vars = {
    "DATABASE_TYPE": os.getenv("DATABASE_TYPE", "Not Set"),
    "POSTGRES_DATABASE_URL": os.getenv("POSTGRES_DATABASE_URL", "Not Set"),
    "DATABASE_URL": os.getenv("DATABASE_URL", "Not Set"),
    "SQLITE_DATABASE_URL": os.getenv("SQLITE_DATABASE_URL", "Not Set")
}

for key, value in env_vars.items():
    if "postgresql" in str(value):
        print(f"   ✅ {key}: PostgreSQL URL (Hidden for security)")
    elif "sqlite" in str(value):
        print(f"   🗃️ {key}: {value}")
    elif value == "Not Set":
        print(f"   ❌ {key}: Not Set")
    else:
        print(f"   📝 {key}: {value}")

# 2. Dependencies Check
print("\n2. 📦 Database Dependencies Check:")
dependencies = {
    "psycopg2": None,
    "asyncpg": None,
    "sqlalchemy": None
}

for dep in dependencies:
    try:
        module = __import__(dep.replace("-", "_"))
        dependencies[dep] = getattr(module, '__version__', 'Available')
        print(f"   ✅ {dep}: {dependencies[dep]}")
    except ImportError:
        dependencies[dep] = "Not Installed"
        print(f"   ❌ {dep}: Not Installed")

# 3. Database Module Test
print("\n3. 🔧 Database Module Test:")
try:
    from app.db.database import get_database_info, test_connection, FINAL_DATABASE_URL
    
    print(f"   📍 Final Database URL: {FINAL_DATABASE_URL.split('@')[0] + '@***' if '@' in FINAL_DATABASE_URL else FINAL_DATABASE_URL}")
    
    # Get database info
    db_info = get_database_info()
    print(f"   📊 Database Type: {db_info.get('type', 'Unknown')}")
    print(f"   🔗 Connection Status: {db_info.get('is_connected', False)}")
    print(f"   🚗 Driver: {db_info.get('engine_info', {}).get('driver', 'Unknown')}")
    print(f"   🏠 Host: {db_info.get('engine_info', {}).get('host', 'Unknown')}")
    
    # Test connection
    connection_result = test_connection()
    print(f"   🧪 Connection Test: {'✅ Success' if connection_result else '❌ Failed'}")
    
except Exception as e:
    print(f"   ❌ Database Module Error: {e}")

# 4. Neon DB Direct Connection Test
print("\n4. 🐘 Neon DB Direct Connection Test:")
neon_url = os.getenv("POSTGRES_DATABASE_URL")
if neon_url:
    try:
        import psycopg2
        
        # Parse URL for connection
        if neon_url.startswith("postgresql://"):
            print("   🔗 Attempting direct Neon DB connection...")
            
            # Test connection with psycopg2
            conn = psycopg2.connect(neon_url, sslmode='require', connect_timeout=30)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            print(f"   ✅ Direct Neon DB Connection: Success")
            print(f"   📄 PostgreSQL Version: {version[0] if version else 'Unknown'}")
            
    except Exception as e:
        print(f"   ❌ Direct Neon DB Connection Failed: {e}")
        
        if "timeout" in str(e).lower():
            print("   💡 Solution: Check network connectivity or Neon DB status")
        elif "authentication" in str(e).lower():
            print("   💡 Solution: Verify credentials in .env file")
        elif "ssl" in str(e).lower():
            print("   💡 Solution: SSL configuration issue")
else:
    print("   ❌ No Neon DB URL found in environment variables")

# 5. SQLite Current Status
print("\n5. 🗃️ SQLite Current Status:")
sqlite_path = "./airiss_v4.db"
if os.path.exists(sqlite_path):
    file_size = os.path.getsize(sqlite_path)
    print(f"   ✅ SQLite File Exists: {sqlite_path}")
    print(f"   📏 File Size: {file_size / 1024:.2f} KB")
    
    # Check if it has data
    try:
        import sqlite3
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        print(f"   📊 Tables Found: {len(tables)}")
        for table in tables:
            print(f"      - {table[0]}")
            
    except Exception as e:
        print(f"   ❌ SQLite Check Error: {e}")
else:
    print(f"   ❌ SQLite File Not Found: {sqlite_path}")

# 6. Recommendations
print("\n6. 💡 Recommendations:")

if env_vars["DATABASE_TYPE"] == "postgres" and neon_url:
    if dependencies["psycopg2"] == "Not Installed":
        print("   🔧 Install psycopg2: pip install psycopg2-binary")
    else:
        print("   🔧 Check database.py logic for PostgreSQL selection")
        print("   🔧 Verify Neon DB connectivity and credentials")
else:
    print("   🔧 Set DATABASE_TYPE=postgres in .env file")
    print("   🔧 Set POSTGRES_DATABASE_URL with valid Neon DB URL")

print("\n" + "=" * 60)
print("🎯 Diagnosis Complete")
print("=" * 60)
