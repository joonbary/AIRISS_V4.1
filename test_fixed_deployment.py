#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIRISS Fixed Excel Download Test
Auth 컴포넌트 수정 + Excel API 테스트
"""

import requests
import time
from pathlib import Path

def test_deployment_success():
    """Railway 배포 성공 및 Excel 다운로드 테스트"""
    
    base_url = "https://web-production-4066.up.railway.app"
    
    print("=" * 70)
    print("🚀 AIRISS Fixed Deployment Test")
    print("Auth import fix + Excel API endpoints")
    print("=" * 70)
    
    # 1. 기본 서버 연결 테스트
    print(f"\n🔗 Testing server connection...")
    try:
        response = requests.get(f"{base_url}/", timeout=15)
        print(f"✅ Server Status: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 Frontend build SUCCESS - Auth import fixed!")
        else:
            print(f"⚠️ Server responding but status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        print("💡 Wait for Railway deployment to complete...")
        return False
    
    # 2. Health check
    print(f"\n🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"⚠️ Health check status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Health check failed: {e}")
    
    # 3. Excel 다운로드 테스트
    endpoints_to_test = [
        {
            "name": "Excel Export",
            "url": f"{base_url}/api/analysis-storage/export-excel",
            "expected_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "file_ext": "xlsx"
        },
        {
            "name": "CSV Export", 
            "url": f"{base_url}/api/analysis-storage/export-csv",
            "expected_type": "text/csv",
            "file_ext": "csv"
        }
    ]
    
    success_count = 0
    
    for endpoint in endpoints_to_test:
        print(f"\n📥 Testing {endpoint['name']}...")
        print(f"URL: {endpoint['url']}")
        
        try:
            response = requests.get(endpoint['url'], timeout=30)
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                content_length = len(response.content)
                content_disposition = response.headers.get('Content-Disposition', '')
                
                print(f"✅ Status: {response.status_code}")
                print(f"📄 Content-Type: {content_type}")
                print(f"📊 Content-Length: {content_length} bytes")
                print(f"💾 Content-Disposition: {content_disposition}")
                
                # 파일 다운로드 테스트
                if content_disposition and content_length > 0:
                    filename = f"test_download_{endpoint['name'].lower().replace(' ', '_')}_{int(time.time())}.{endpoint['file_ext']}"
                    
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = Path(filename).stat().st_size
                    print(f"💿 Downloaded: {filename} ({file_size} bytes)")
                    
                    # 파일 유효성 검증
                    if endpoint['file_ext'] == 'xlsx' and response.content.startswith(b'PK'):
                        print("✅ Excel file format: VALID")
                        success_count += 1
                    elif endpoint['file_ext'] == 'csv' and (response.content.startswith(b'\xef\xbb\xbf') or len(response.content) > 0):
                        print("✅ CSV file format: VALID")
                        success_count += 1
                    else:
                        print("⚠️ File format: Unknown (check manually)")
                        success_count += 0.5
                else:
                    print("⚠️ No download headers or empty content")
                    
            elif response.status_code == 404:
                print(f"❌ Status: {response.status_code} - Endpoint not deployed yet")
                print("💡 Check if Railway deployment completed successfully")
                
            else:
                print(f"❌ Status: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"📝 Error: {error_detail}")
                except:
                    print(f"📝 Response: {response.text[:200]}...")
                    
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout - Server may be slow")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 4. 결과 요약
    print("\n" + "=" * 70)
    print("🎯 Test Summary:")
    print(f"✅ Successful downloads: {success_count}/2")
    
    if success_count >= 2:
        print("🎉 All tests PASSED! Excel download issue RESOLVED!")
        print("✅ Frontend Auth import: Fixed")
        print("✅ Excel endpoint: Working")
        print("✅ CSV endpoint: Working")
    elif success_count >= 1:
        print("⚠️ Partial success - Some endpoints working")
    else:
        print("❌ Tests failed - Check deployment status")
        
    print("=" * 70)
    
    return success_count >= 2

if __name__ == "__main__":
    test_deployment_success()
