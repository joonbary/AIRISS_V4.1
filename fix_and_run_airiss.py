#!/usr/bin/env python3
"""
AIRISS v4.1 모듈 경로 문제 해결 및 서버 실행
"""

import sys
import os
from pathlib import Path

def fix_module_path():
    """Python 모듈 경로 문제 해결"""
    # 현재 스크립트의 부모 디렉토리를 프로젝트 루트로 설정
    project_root = Path(__file__).parent.absolute()
    
    # sys.path에 프로젝트 루트 추가 (최우선)
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # PYTHONPATH 환경변수도 설정
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if str(project_root) not in current_pythonpath:
        new_pythonpath = f"{project_root}{os.pathsep}{current_pythonpath}" if current_pythonpath else str(project_root)
        os.environ['PYTHONPATH'] = new_pythonpath
    
    print(f"🔧 프로젝트 루트: {project_root}")
    print(f"🐍 Python 경로 설정 완료")
    print(f"📁 sys.path[0]: {sys.path[0]}")
    print(f"🌍 PYTHONPATH: {os.environ.get('PYTHONPATH', 'NOT SET')}")
    print()

def test_imports():
    """모듈 import 테스트"""
    try:
        print("🧪 모듈 import 테스트...")
        
        # 핵심 모듈들 import 테스트
        from app.db.database import get_database_service
        print("✅ 데이터베이스 모듈 로드 성공")
        
        from app.api.analysis import router as analysis_router
        print("✅ 분석 API 모듈 로드 성공")
        
        from app.api.upload import router as upload_router
        print("✅ 업로드 API 모듈 로드 성공")
        
        from app.services.airiss_hybrid_analyzer import AIRISSHybridAnalyzer
        print("✅ 하이브리드 분석기 모듈 로드 성공")
        
        print("🎉 모든 핵심 모듈 로드 성공!")
        return True
        
    except ImportError as e:
        print(f"❌ 모듈 import 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def run_server():
    """AIRISS 서버 실행"""
    try:
        print("🚀 AIRISS v4.1 서버 시작...")
        print("📱 브라우저에서 http://localhost:8002 접속하세요")
        print("🛑 서버 종료: Ctrl+C")
        print("=" * 50)
        
        # main.py 실행
        from app.main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8002,
            reload=False,  # 안정성을 위해 reload 비활성화
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 서버 종료됨")
    except Exception as e:
        print(f"❌ 서버 실행 오류: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🎯 AIRISS v4.1 모듈 경로 문제 해결 도구")
    print("=" * 50)
    
    # 1. 모듈 경로 수정
    fix_module_path()
    
    # 2. 모듈 import 테스트
    if test_imports():
        # 3. 서버 실행
        run_server()
    else:
        print("❌ 모듈 로드 실패로 서버를 시작할 수 없습니다.")
        print("🔧 다음 사항을 확인해주세요:")
        print("   1. 필요한 패키지가 모두 설치되었는지")
        print("   2. .env 파일이 올바르게 설정되었는지")
        print("   3. Python 버전이 3.8+ 인지")
        
        input("Enter 키를 눌러 종료...")
