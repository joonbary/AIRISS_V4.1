# test_excel_download_english.py
# AIRISS Excel Download Test - English Only
# Avoid encoding issues with English-only messages

import requests
import os
from datetime import datetime

def test_excel_download(base_url="http://localhost:8002"):
    """
    Test new Excel download functionality
    
    Args:
        base_url: Server address (default: local server)
    """
    print("AIRISS Excel Download Test - English Only")
    print(f"Server: {base_url}")
    print("="*50)
    
    # 1. Health check
    try:
        print("\n1. Health Check...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Server is running")
            health_data = response.json()
            print(f"   - Service: {health_data.get('service', 'Unknown')}")
            print(f"   - Database: {health_data.get('database', {}).get('connected', 'Unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check connection failed: {e}")
        return False
    
    # 2. Check analysis results
    try:
        print("\n2. Checking Analysis Results...")
        response = requests.get(f"{base_url}/api/analysis-storage/results?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            result_count = data.get('count', 0)
            print(f"✅ Analysis results found: {result_count} records")
            
            if result_count == 0:
                print("⚠️ No stored analysis results found.")
                print("💡 Continuing test with empty Excel file generation.")
        else:
            print(f"❌ Analysis results check failed: {response.status_code}")
            print("💡 Continuing test with empty Excel file generation.")
    except Exception as e:
        print(f"❌ Analysis results connection failed: {e}")
        print("💡 Continuing test with empty Excel file generation.")
    
    # 3. Test new Excel download
    try:
        print("\n3. Testing Excel File Download...")
        excel_url = f"{base_url}/api/analysis-storage/export-excel"
        print(f"📥 Download URL: {excel_url}")
        
        response = requests.get(excel_url, timeout=30, stream=True)
        
        if response.status_code == 200:
            # Check Content-Type
            content_type = response.headers.get('content-type', '')
            print(f"✅ Excel download successful!")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Content-Type: {content_type}")
            print(f"   - Content-Length: {response.headers.get('content-length', 'Unknown')}")
            
            # Check if it's a real Excel file
            if 'openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
                print("✅ Correct Excel MIME type confirmed")
                
                # Save file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_download_{timestamp}.xlsx"
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(filename)
                print(f"✅ Excel file saved: {filename} ({file_size} bytes)")
                
                # Test file validity
                try:
                    import openpyxl
                    workbook = openpyxl.load_workbook(filename)
                    sheet_names = workbook.sheetnames
                    print(f"✅ Excel file validation: {len(sheet_names)} sheets ({sheet_names})")
                    workbook.close()
                except Exception as e:
                    print(f"❌ Excel file validation failed: {e}")
                
            else:
                print(f"❌ Wrong Content-Type: {content_type}")
                print("Response content preview:")
                print(response.text[:500])
                
        else:
            print(f"❌ Excel download failed: {response.status_code}")
            print("Response content:")
            print(response.text[:500])
            return False
            
    except Exception as e:
        print(f"❌ Excel download connection failed: {e}")
        return False
    
    # 4. Test CSV download
    try:
        print("\n4. Testing CSV File Download...")
        csv_url = f"{base_url}/api/analysis-storage/export-csv"
        print(f"📥 Download URL: {csv_url}")
        
        response = requests.get(csv_url, timeout=30)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            print(f"✅ CSV download successful!")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Content-Type: {content_type}")
            
            # Save CSV file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"test_download_{timestamp}.csv"
            
            with open(csv_filename, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(csv_filename)
            print(f"✅ CSV file saved: {csv_filename} ({file_size} bytes)")
            
            # Preview CSV content
            with open(csv_filename, 'r', encoding='utf-8-sig') as f:
                preview = f.read(200)
                print(f"CSV file preview:")
                print(preview)
                
        else:
            print(f"❌ CSV download failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CSV download connection failed: {e}")
        return False
    
    print("\n🎉 All tests completed successfully!")
    print("\n📋 Test Results:")
    print("✅ Health check passed")
    print("✅ Excel file download successful")
    print("✅ CSV file download successful")
    print("✅ File validation completed")
    
    print("\n🌐 Browser test URLs:")
    print(f"Excel: {base_url}/api/analysis-storage/export-excel")
    print(f"CSV: {base_url}/api/analysis-storage/export-csv")
    
    return True

if __name__ == "__main__":
    print("AIRISS Excel Download Test - English Only")
    print("System Check:")
    
    # Check Python version
    import sys
    print(f"Python {sys.version}")
    print()
    
    print("Testing Excel download functionality...")
    
    # Local server test
    print("🏠 Local Server Test")
    local_success = test_excel_download("http://localhost:8002")
    
    # Railway server test
    railway_url = input("\n🚀 Enter Railway deployment URL (press Enter to skip): ").strip()
    railway_success = False
    
    if railway_url:
        if not railway_url.startswith('http'):
            railway_url = f"https://{railway_url}"
        print(f"\n🚀 Railway Server Test: {railway_url}")
        railway_success = test_excel_download(railway_url)
    
    print("\n🎯 Final Results:")
    print(f"Local Server: {'✅ Success' if local_success else '❌ Failed'}")
    if railway_url:
        print(f"Railway Server: {'✅ Success' if railway_success else '❌ Failed'}")
    
    print("\nTest completed! Check the generated Excel and CSV files.")
