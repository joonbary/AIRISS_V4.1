#!/usr/bin/env python3
"""
Simple database connection test for AIRISS v4.1
English only, no special characters
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

print("=" * 50)
print("AIRISS Database Connection Test")
print("=" * 50)

try:
    from app.db.database import get_database_info, test_connection
    
    print("\nTesting database connection...")
    
    # Get database info
    db_info = get_database_info()
    
    print(f"Connection Type: {db_info.get('type', 'Unknown')}")
    print(f"Connected: {db_info.get('is_connected', False)}")
    print(f"Driver: {db_info.get('engine_info', {}).get('driver', 'Unknown')}")
    print(f"Host: {db_info.get('engine_info', {}).get('host', 'Unknown')}")
    
    # Test connection
    connection_result = test_connection()
    print(f"Connection Test: {'SUCCESS' if connection_result else 'FAILED'}")
    
    # Check if PostgreSQL
    if db_info.get('type') == 'postgresql':
        print("\nSUCCESS: Neon DB (PostgreSQL) connection working!")
        print("Your AIRISS system is now using cloud database")
    elif db_info.get('type') == 'sqlite':
        print("\nFALLBACK: Using SQLite database")
        print("PostgreSQL connection may need troubleshooting")
    else:
        print(f"\nUNKNOWN: Connection type is {db_info.get('type')}")
    
except Exception as e:
    print(f"\nERROR: Database test failed - {e}")
    print("The enhanced database module may have issues")

print("\n" + "=" * 50)
print("Test completed")
print("=" * 50)
