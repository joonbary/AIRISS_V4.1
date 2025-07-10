#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIRISS v5.0 인코딩 문제 진단 및 해결 스크립트
"""

import os
import sys
import locale
import subprocess
from pathlib import Path

def diagnose_encoding():
    """인코딩 환경 진단"""
    print("🔍 인코딩 환경 진단 시작")
    print("=" * 60)
    
    # 1. 시스템 인코딩 정보
    print("\n1️⃣ 시스템 인코딩 정보:")
    print(f"✅ Python 버전: {sys.version}")
    print(f"✅ 기본 인코딩: {sys.getdefaultencoding()}")
    print(f"✅ 파일시스템 인코딩: {sys.getfilesystemencoding()}")
    print(f"✅ 로케일 인코딩: {locale.getpreferredencoding()}")
    
    if hasattr(sys.stdout, 'encoding'):
        print(f"✅ stdout 인코딩: {sys.stdout.encoding}")
    if hasattr(sys.stderr, 'encoding'):
        print(f"✅ stderr 인코딩: {sys.stderr.encoding}")
    
    # 2. 환경 변수 확인
    print("\n2️⃣ 환경 변수 확인:")
    encoding_vars = ['PYTHONIOENCODING', 'PYTHONPATH', 'LANG', 'LC_ALL']
    for var in encoding_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️ {var}: 설정되지 않음")
    
    # 3. 현재 디렉토리 경로 확인
    print("\n3️⃣ 경로 인코딩 확인:")
    current_dir = os.getcwd()
    print(f"✅ 현재 디렉토리: {current_dir}")
    
    # 한글 경로 확인
    if any(ord(c) > 127 for c in current_dir):
        print("⚠️ 경로에 한글/특수문자가 포함되어 있습니다.")
        print("💡 영어 경로로 이동하는 것을 권장합니다.")
    else:
        print("✅ 경로에 한글/특수문자 없음")
    
    # 4. 파일 경로 테스트
    print("\n4️⃣ 파일 경로 테스트:")
    test_files = ['app/main.py', 'start_airiss_v5.bat', 'requirements.txt']
    for file_path in test_files:
        try:
            path = Path(file_path)
            if path.exists():
                print(f"✅ {file_path}: 존재함")
                # 파일 읽기 테스트
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        f.read(100)  # 처음 100자만 읽기
                    print(f"   └─ UTF-8 읽기 성공")
                except Exception as e:
                    print(f"   └─ UTF-8 읽기 실패: {e}")
            else:
                print(f"❌ {file_path}: 존재하지 않음")
        except Exception as e:
            print(f"❌ {file_path}: 경로 오류 - {e}")
    
    # 5. Python 모듈 import 테스트
    print("\n5️⃣ Python 모듈 import 테스트:")
    try:
        # 현재 디렉토리를 Python path에 추가
        sys.path.insert(0, os.getcwd())
        import app
        print("✅ app 모듈 import 성공")
    except Exception as e:
        print(f"❌ app 모듈 import 실패: {e}")
    
    # 6. 코드페이지 확인 (Windows)
    if os.name == 'nt':
        print("\n6️⃣ Windows 코드페이지 확인:")
        try:
            result = subprocess.run(['chcp'], capture_output=True, text=True, shell=True)
            print(f"✅ 현재 코드페이지: {result.stdout.strip()}")
        except Exception as e:
            print(f"❌ 코드페이지 확인 실패: {e}")
    
    print("\n🎯 권장 해결책:")
    print("1. 환경 변수 설정: set PYTHONIOENCODING=utf-8")
    print("2. 코드페이지 변경: chcp 65001")
    print("3. 영어 경로로 프로젝트 이동")
    print("4. PowerShell 대신 CMD 사용")

if __name__ == "__main__":
    diagnose_encoding()
