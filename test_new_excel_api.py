#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIRISS Excel Download Test Script
새로운 Excel/CSV 엔드포인트 테스트용
"""

import requests
import time
from pathlib import Path

def test_excel_download():
    """실제 Excel 파일 다운로드 테스트"""
    
    # 테스트할 URL들
    base_urls = [
        "http://localhost:8002",  # 로컬 서버
        "https://web-production-4066.up.railway.app"  # Railway 서버
    ]
    
    endpoints = {
        "excel": "/api/analysis-storage/export-excel",
        "csv": "/api/analysis-storage/export-csv",
        "old": "/api/analysis-storage/export"  # 기존 엔드포인트 (비교용)
    }
    
    print("=" * 60)
    print("🧪 AIRISS Excel/CSV Download Test")
    print("=" * 60)
    
    for base_url in base_urls:
        print(f"\n🔗 Testing: {base_url}")
        print("-" * 40)
        
        # 서버 연결 테스트
        try:
            response = requests.get(f"{base_url}/", timeout=10)
            print(f"✅ Server connection: OK (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Server connection: FAILED ({e})")
            continue
        
        # 각 엔드포인트 테스트
        for name, endpoint in endpoints.items():
            url = f"{base_url}{endpoint}"
            
            try:
                print(f"\n📥 Testing {name.upper()} download...")
                print(f"URL: {url}")
                
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '')
                    content_length = len(response.content)
                    
                    print(f"✅ Status: {response.status_code}")
                    print(f"📄 Content-Type: {content_type}")
                    print(f"📊 Content-Length: {content_length} bytes")
                    
                    # Content-Disposition 헤더 확인 (파일 다운로드)
                    content_disposition = response.headers.get('Content-Disposition', '')
                    if content_disposition:
                        print(f"💾 Content-Disposition: {content_disposition}")
                        
                        # 실제 파일 저장 테스트
                        if name in ['excel', 'csv']:
                            extension = 'xlsx' if name == 'excel' else 'csv'
                            filename = f"test_download_{name}_{int(time.time())}.{extension}"
                            
                            with open(filename, 'wb') as f:
                                f.write(response.content)
                            
                            file_size = Path(filename).stat().st_size
                            print(f"💿 Saved to: {filename} ({file_size} bytes)")
                            
                            # 파일 검증
                            if name == 'excel' and response.content.startswith(b'PK'):
                                print("✅ Excel file format: VALID (ZIP-based)")
                            elif name == 'csv' and response.content.startswith(b'\xef\xbb\xbf'):
                                print("✅ CSV file format: VALID (BOM detected)")
                            else:
                                print("⚠️ File format: Check manually")
                    else:
                        print("⚠️ No Content-Disposition header (may not trigger download)")
                        
                        # 응답 내용 미리보기 (텍스트인 경우)
                        if 'json' in content_type or 'text' in content_type:
                            preview = response.text[:200]
                            print(f"📝 Response preview: {preview}...")
                
                elif response.status_code == 404:
                    print(f"❌ Status: {response.status_code} - Endpoint not found")
                    print("💡 API may not be deployed yet")
                
                else:
                    print(f"❌ Status: {response.status_code}")
                    try:
                        error_detail = response.json()
                        print(f"📝 Error: {error_detail}")
                    except:
                        print(f"📝 Response: {response.text[:200]}...")
                        
            except requests.exceptions.ConnectRefused:
                print(f"❌ Connection refused - Server not running")
            except requests.exceptions.Timeout:
                print(f"❌ Request timeout - Server may be slow")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("✅ Excel endpoint should return .xlsx file")
    print("✅ CSV endpoint should return .csv file with BOM")
    print("⚠️ Old endpoint returns JSON/text (not actual file)")
    print("=" * 60)

if __name__ == "__main__":
    test_excel_download()
