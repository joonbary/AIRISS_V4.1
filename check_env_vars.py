# -*- coding: utf-8 -*-
"""
환경변수 로딩 상태 확인
"""

import os
from dotenv import load_dotenv

def check_environment_variables():
    """환경변수 상태 확인"""
    print("🔍 환경변수 로딩 상태 확인")
    print("=" * 50)
    
    # 1. .env 파일 로딩 시도
    print("1. .env 파일 로딩...")
    load_result = load_dotenv('.env', override=True)
    print(f"   로딩 결과: {load_result}")
    
    # 2. 핵심 환경변수 확인
    print("\n2. 핵심 환경변수 값:")
    
    env_vars = [
        "DATABASE_TYPE",
        "POSTGRES_DATABASE_URL", 
        "DATABASE_URL",
        "SQLITE_DATABASE_URL"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "NOT_SET")
        if "password" in var.lower() or "url" in var.lower():
            # 민감한 정보는 일부만 표시
            if value and len(value) > 10:
                masked_value = value[:20] + "***" + value[-10:]
                print(f"   {var}: {masked_value}")
            else:
                print(f"   {var}: {value}")
        else:
            print(f"   {var}: {value}")
    
    # 3. .env 파일 내용 직접 읽기
    print("\n3. .env 파일 직접 읽기:")
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10], 1):  # 처음 10줄만
                line = line.strip()
                if line and not line.startswith('#'):
                    if "DATABASE" in line:
                        print(f"   Line {i}: {line}")
    except Exception as e:
        print(f"   .env 파일 읽기 실패: {e}")
    
    # 4. 올바른 설정 제안
    print("\n4. 권장 설정:")
    print("   DATABASE_TYPE=postgres")
    print("   POSTGRES_DATABASE_URL=postgresql://neondb_owner:***")
    print("   DATABASE_URL=postgresql+psycopg2://neondb_owner:***")
    
    return load_result

if __name__ == "__main__":
    check_environment_variables()
    input("\n아무 키나 눌러 종료...")
