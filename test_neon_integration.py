# Neon DB Integration Test
# Test PostgreSQL Analysis Storage Service

import sys
import os
import asyncio
from datetime import datetime

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_postgresql_storage_service():
    """Test PostgreSQL Analysis Storage Service"""
    
    print("=" * 60)
    print("NEON DB INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Import the new service
        from app.services.analysis_storage_service_postgresql import PostgreSQLAnalysisStorageService
        
        print("1. Creating PostgreSQL Storage Service...")
        service = PostgreSQLAnalysisStorageService()
        
        if not service.is_available():
            print("   ERROR: Service not available!")
            return False
        
        print("   SUCCESS: Service created")
        
        # Test database connection
        print("\n2. Testing database connection...")
        health = service.get_storage_health()
        print(f"   Status: {health.get('status')}")
        print(f"   Database Type: {health.get('database_info', {}).get('type')}")
        print(f"   Total Results: {health.get('total_analysis_results', 0)}")
        
        if health.get('status') != 'healthy':
            print("   ERROR: Database connection failed!")
            return False
        
        print("   SUCCESS: Database connected")
        
        # Test saving analysis result
        print("\n3. Testing save analysis result...")
        test_data = {
            'uid': 'TEST001',
            'file_id': 'test_file_001',
            'filename': 'test_file.xlsx',
            'opinion': 'This is a test opinion for PostgreSQL integration',
            'hybrid_score': 85.5,
            'text_score': 80.0,
            'quantitative_score': 90.0,
            'ok_grade': 'A',
            'confidence': 0.92,
            'analysis_mode': 'hybrid',
            'version': '4.1'
        }
        
        analysis_id = service.save_analysis_result(test_data)
        print(f"   Analysis ID: {analysis_id}")
        
        if not analysis_id:
            print("   ERROR: Failed to save analysis result!")
            return False
        
        print("   SUCCESS: Analysis result saved")
        
        # Test retrieving analysis result
        print("\n4. Testing get analysis result...")
        retrieved = service.get_analysis_by_id(analysis_id)
        
        if not retrieved:
            print("   ERROR: Failed to retrieve analysis result!")
            return False
        
        print(f"   UID: {retrieved.get('uid')}")
        print(f"   Score: {retrieved.get('hybrid_score')}")
        print(f"   Grade: {retrieved.get('ok_grade')}")
        print("   SUCCESS: Analysis result retrieved")
        
        # Test analysis statistics
        print("\n5. Testing analysis statistics...")
        stats = service.get_analysis_statistics(days=7)
        
        if 'error' in stats:
            print(f"   ERROR: {stats['error']}")
            return False
        
        print(f"   Total Analyses: {stats.get('total_analyses', 0)}")
        print(f"   Average Score: {stats.get('average_score', 0)}")
        print(f"   Storage Mode: {stats.get('storage_mode')}")
        print("   SUCCESS: Statistics retrieved")
        
        # Test search functionality
        print("\n6. Testing search functionality...")
        search_results = service.search_analysis_results('test', 'all', limit=10)
        print(f"   Search Results: {len(search_results)} found")
        print("   SUCCESS: Search completed")
        
        # Test cleanup (dry run)
        print("\n7. Testing cleanup functionality...")
        service_info = service.get_storage_info()
        print(f"   Service Type: {service_info.get('service_type')}")
        print(f"   PostgreSQL Only: {service_info.get('postgresql_only')}")
        print(f"   SQLite Removed: {service_info.get('sqlite_removed')}")
        print(f"   Unified Database: {service_info.get('unified_database')}")
        print("   SUCCESS: Service info retrieved")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED - NEON DB INTEGRATION SUCCESSFUL!")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"   ERROR: Import failed - {e}")
        return False
    except Exception as e:
        print(f"   ERROR: Test failed - {e}")
        return False

def test_database_connection():
    """Test basic database connection"""
    
    print("\nDATABASE CONNECTION TEST")
    print("-" * 40)
    
    try:
        from app.db.database import get_database_info, test_connection
        
        # Get database info
        db_info = get_database_info()
        print(f"Connection Type: {db_info.get('type')}")
        print(f"Connected: {db_info.get('is_connected')}")
        print(f"Driver: {db_info.get('engine_info', {}).get('driver')}")
        print(f"Host: {db_info.get('engine_info', {}).get('host')}")
        
        if db_info.get('type') == 'postgresql':
            print("SUCCESS: PostgreSQL connection confirmed")
            return True
        else:
            print(f"WARNING: Expected PostgreSQL but got {db_info.get('type')}")
            return False
            
    except Exception as e:
        print(f"ERROR: Database connection test failed - {e}")
        return False

if __name__ == "__main__":
    print("Starting Neon DB Integration Tests...")
    print("Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Test 1: Database connection
    connection_ok = test_database_connection()
    
    if not connection_ok:
        print("\nERROR: Database connection failed. Please check your configuration.")
        sys.exit(1)
    
    # Test 2: PostgreSQL storage service
    storage_ok = test_postgresql_storage_service()
    
    if storage_ok:
        print("\nSUCCESS: All tests passed. Neon DB integration is working correctly!")
        print("\nNext steps:")
        print("1. Review test results above")
        print("2. Run integration script to replace old service")
        print("3. Monitor system performance")
    else:
        print("\nERROR: Some tests failed. Please review the error messages above.")
        sys.exit(1)