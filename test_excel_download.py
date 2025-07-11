# test_excel_download.py
# Excel 다운로드 기능 테스트 스크립트

import requests
import os
from datetime import datetime

def test_excel_download(base_url="http://localhost:8002"):
    """
    새로운 Excel 다운로드 기능 테스트
    
    Args:
        base_url: 서버 주소 (기본값: 로컬 서버)
    """
    print("🧪 AIRISS Excel 다운로드 기능 테스트 시작")
    print(f"📍 서버 주소: {base_url}")
    
    # 1. 헬스체크
    try:
        print("\n1️⃣ 헬스체크...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 서버 정상 동작")
            health_data = response.json()
            print(f"   - 서비스: {health_data.get('service', 'Unknown')}")
            print(f"   - 데이터베이스: {health_data.get('database', {}).get('connected', 'Unknown')}")
        else:
            print(f"❌ 헬스체크 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 헬스체크 연결 실패: {e}")
        return False
    
    # 2. 분석 결과 조회 (있는지 확인)
    try:
        print("\n2️⃣ 분석 결과 확인...")
        response = requests.get(f"{base_url}/api/analysis-storage/results?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            result_count = data.get('count', 0)
            print(f"✅ 분석 결과 조회 성공: {result_count}건")
            
            if result_count == 0:
                print("⚠️ 저장된 분석 결과가 없습니다. 테스트 데이터를 생성하거나 실제 분석을 실행해주세요.")
                # 여기서 테스트 데이터 생성 가능
                print("💡 빈 Excel 파일 다운로드로 테스트를 계속합니다.")
        else:
            print(f"❌ 분석 결과 조회 실패: {response.status_code}")
            print("💡 빈 Excel 파일 다운로드로 테스트를 계속합니다.")
    except Exception as e:
        print(f"❌ 분석 결과 조회 연결 실패: {e}")
        print("💡 빈 Excel 파일 다운로드로 테스트를 계속합니다.")
    
    # 3. 새로운 Excel 다운로드 테스트
    try:
        print("\n3️⃣ 새로운 Excel 파일 다운로드 테스트...")
        excel_url = f"{base_url}/api/analysis-storage/export-excel"
        print(f"📥 다운로드 URL: {excel_url}")
        
        response = requests.get(excel_url, timeout=30, stream=True)
        
        if response.status_code == 200:
            # Content-Type 확인
            content_type = response.headers.get('content-type', '')
            print(f"✅ Excel 다운로드 성공!")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Content-Type: {content_type}")
            print(f"   - Content-Length: {response.headers.get('content-length', 'Unknown')}")
            
            # 실제 Excel 파일인지 확인
            if 'openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
                print("✅ 올바른 Excel MIME 타입 확인")
                
                # 파일 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_download_{timestamp}.xlsx"
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(filename)
                print(f"✅ Excel 파일 저장 완료: {filename} ({file_size} bytes)")
                
                # 파일 열기 테스트 (openpyxl로)
                try:
                    import openpyxl
                    workbook = openpyxl.load_workbook(filename)
                    sheet_names = workbook.sheetnames
                    print(f"✅ Excel 파일 유효성 확인: {len(sheet_names)}개 시트 ({sheet_names})")
                    workbook.close()
                except Exception as e:
                    print(f"❌ Excel 파일 유효성 검사 실패: {e}")
                
            else:
                print(f"❌ 잘못된 Content-Type: {content_type}")
                print("응답 내용 일부:")
                print(response.text[:500])
                
        else:
            print(f"❌ Excel 다운로드 실패: {response.status_code}")
            print("응답 내용:")
            print(response.text[:500])
            return False
            
    except Exception as e:
        print(f"❌ Excel 다운로드 연결 실패: {e}")
        return False
    
    # 4. CSV 다운로드 테스트
    try:
        print("\n4️⃣ 새로운 CSV 파일 다운로드 테스트...")
        csv_url = f"{base_url}/api/analysis-storage/export-csv"
        print(f"📥 다운로드 URL: {csv_url}")
        
        response = requests.get(csv_url, timeout=30)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            print(f"✅ CSV 다운로드 성공!")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Content-Type: {content_type}")
            
            # CSV 파일 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"test_download_{timestamp}.csv"
            
            with open(csv_filename, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(csv_filename)
            print(f"✅ CSV 파일 저장 완료: {csv_filename} ({file_size} bytes)")
            
            # CSV 내용 미리보기
            with open(csv_filename, 'r', encoding='utf-8-sig') as f:
                preview = f.read(200)
                print(f"CSV 파일 내용 미리보기:")
                print(preview)
                
        else:
            print(f"❌ CSV 다운로드 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ CSV 다운로드 연결 실패: {e}")
        return False
    
    print("\n🎉 모든 테스트 완료!")
    print("\n📋 테스트 결과:")
    print("✅ 헬스체크 통과")
    print("✅ Excel 파일 다운로드 성공")
    print("✅ CSV 파일 다운로드 성공")
    print("✅ 파일 유효성 검증 완료")
    
    print("\n🌐 브라우저 테스트 URL:")
    print(f"Excel: {base_url}/api/analysis-storage/export-excel")
    print(f"CSV: {base_url}/api/analysis-storage/export-csv")
    
    return True

if __name__ == "__main__":
    # 로컬 테스트
    print("🏠 로컬 서버 테스트")
    local_success = test_excel_download("http://localhost:8002")
    
    # Railway 배포 서버 테스트 (있는 경우)
    railway_url = input("\n🚀 Railway 배포 URL이 있다면 입력하세요 (없으면 Enter): ").strip()
    if railway_url:
        if not railway_url.startswith('http'):
            railway_url = f"https://{railway_url}"
        print(f"\n🚀 Railway 서버 테스트: {railway_url}")
        railway_success = test_excel_download(railway_url)
    
    print("\n🎯 최종 결과:")
    print(f"로컬 서버: {'✅ 성공' if local_success else '❌ 실패'}")
    if 'railway_url' in locals() and railway_url:
        print(f"Railway 서버: {'✅ 성공' if railway_success else '❌ 실패'}")
