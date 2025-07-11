import requests
import sys

def check_api_endpoints(base_url):
    """API 엔드포인트 존재 여부 확인"""
    print(f"🔍 {base_url} API 엔드포인트 확인")
    
    endpoints = [
        "/health",
        "/api",
        "/api/analysis-storage/results", 
        "/api/analysis-storage/export",      # 기존 API
        "/api/analysis-storage/export-excel", # 새로운 Excel API
        "/api/analysis-storage/export-csv"    # 새로운 CSV API
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.head(url, timeout=10)
            
            if response.status_code == 200:
                status = "✅ 존재"
            elif response.status_code == 404:
                status = "❌ 없음"
            elif response.status_code == 405:  # Method not allowed (GET 대신 HEAD)
                status = "✅ 존재 (HEAD 불허)"
            else:
                status = f"⚠️ {response.status_code}"
                
        except Exception as e:
            status = f"❌ 연결실패"
        
        print(f"  {endpoint:<35} {status}")
    
    print()

if __name__ == "__main__":
    print("🧪 AIRISS API 엔드포인트 존재 확인 도구")
    print()
    
    # 로컬 서버 확인
    try:
        check_api_endpoints("http://localhost:8002")
    except:
        print("❌ 로컬 서버 (localhost:8002) 연결 불가")
        print()
    
    # Railway 서버 확인
    railway_url = "https://web-production-4066.up.railway.app"
    try:
        check_api_endpoints(railway_url)
    except:
        print(f"❌ Railway 서버 ({railway_url}) 연결 불가")
    
    print("📋 결론:")
    print("- 새로운 Excel API가 없으면 → Git 푸시 필요")
    print("- 로컬 서버가 연결 안 되면 → 서버 시작 필요")
