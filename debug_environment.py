#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIRISS v5.0 시작 전 환경 점검 스크립트
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_environment():
    """환경 점검"""
    print("🔍 AIRISS v5.0 환경 점검 시작")
    print("=" * 50)
    
    # Python 버전 확인
    print(f"✅ Python 버전: {sys.version}")
    print(f"✅ 작업 디렉토리: {os.getcwd()}")
    print(f"✅ Python 경로: {sys.path[:3]}...")
    
    # 필수 모듈 확인
    required_modules = [
        'fastapi',
        'uvicorn',
        'pandas',
        'numpy',
        'openpyxl'
    ]
    
    print("\n📦 필수 모듈 확인:")
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}: OK")
        except ImportError as e:
            print(f"❌ {module}: 없음 ({e})")
    
    # app 모듈 확인
    print("\n🔍 app 모듈 구조 확인:")
    app_path = Path("app")
    if app_path.exists():
        print(f"✅ app 폴더 존재: {app_path.absolute()}")
        
        # __init__.py 확인
        init_file = app_path / "__init__.py"
        if init_file.exists():
            print(f"✅ app/__init__.py 존재")
        else:
            print(f"❌ app/__init__.py 없음")
        
        # main.py 확인
        main_file = app_path / "main.py"
        if main_file.exists():
            print(f"✅ app/main.py 존재")
        else:
            print(f"❌ app/main.py 없음")
            
        # 서브 모듈들 확인
        sub_modules = ['api', 'core', 'db', 'services', 'utils']
        for sub_module in sub_modules:
            sub_path = app_path / sub_module
            if sub_path.exists():
                print(f"✅ app/{sub_module} 존재")
            else:
                print(f"⚠️ app/{sub_module} 없음")
    else:
        print(f"❌ app 폴더 없음")
    
    # Python path에 app 모듈 추가 시도
    print("\n🔧 app 모듈 import 테스트:")
    try:
        # 현재 디렉토리를 Python path에 추가
        sys.path.insert(0, os.getcwd())
        
        # app 모듈 import 시도
        import app
        print(f"✅ app 모듈 import 성공: {app}")
        
        # app.main import 시도
        from app import main
        print(f"✅ app.main 모듈 import 성공")
        
        # FastAPI app 인스턴스 확인
        if hasattr(main, 'app'):
            print(f"✅ FastAPI app 인스턴스 발견: {main.app}")
        else:
            print(f"❌ FastAPI app 인스턴스 없음")
            
    except Exception as e:
        print(f"❌ app 모듈 import 실패: {e}")
    
    # 환경 변수 확인
    print("\n🌍 환경 변수 확인:")
    env_vars = ['PORT', 'SERVER_PORT', 'REACT_BUILD_PATH', 'PYTHONPATH']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: 설정되지 않음")
    
    print("\n🎯 권장 실행 명령:")
    print("1. uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload")
    print("2. python -m uvicorn app.main:app --host 0.0.0.0 --port 8002")
    print("3. python -c \"from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8002)\"")

if __name__ == "__main__":
    check_environment()
