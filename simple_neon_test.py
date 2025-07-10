# -*- coding: utf-8 -*-
"""
AIRISS 네온 DB 간단 연결 테스트 (Python 3.13 호환)
SQLAlchemy 없이 psycopg2만 사용
"""

import os
import sys
from datetime import datetime

def load_env_manual():
    """수동 .env 파일 파싱"""
    env_vars = {}
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        return env_vars
    except FileNotFoundError:
        print("❌ .env 파일을 찾을 수 없습니다.")
        return {}
    except Exception as e:
        print(f"❌ .env 파일 읽기 오류: {e}")
        return {}

def test_psycopg2_only():
    """psycopg2만으로 네온 DB 연결 테스트"""
    print("🚀 네온 DB 간단 연결 테스트 시작")
    print("=" * 50)
    
    # 1. psycopg2 패키지 확인
    try:
        import psycopg2
        print("✅ psycopg2 패키지 로드 성공")
    except ImportError:
        print("❌ psycopg2 패키지가 설치되지 않았습니다.")
        print("💡 설치 명령: pip install psycopg2-binary")
        return False
    
    # 2. 환경변수 로드
    print("\n🔧 환경변수 로드...")
    env_vars = load_env_manual()
    
    if not env_vars:
        print("❌ 환경변수 로드 실패")
        return False
    
    postgres_url = env_vars.get('POSTGRES_DATABASE_URL', '')
    if not postgres_url:
        print("❌ POSTGRES_DATABASE_URL이 설정되지 않았습니다.")
        return False
    
    print(f"✅ PostgreSQL URL: {postgres_url.split('@')[0]}@***")
    
    # 3. 연결 테스트
    print("\n🔌 네온 DB 연결 테스트...")
    try:
        # 연결 생성
        conn = psycopg2.connect(postgres_url)
        print("✅ 네온 DB 연결 성공!")
        
        # 커서 생성
        cursor = conn.cursor()
        
        # 4. 기본 쿼리 테스트
        print("\n📊 기본 쿼리 테스트...")
        
        # PostgreSQL 버전 확인
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL 버전: {version[:60]}...")
        
        # 현재 시간
        cursor.execute("SELECT current_timestamp;")
        timestamp = cursor.fetchone()[0]
        print(f"✅ 서버 시간: {timestamp}")
        
        # 현재 데이터베이스와 사용자
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"✅ 데이터베이스: {db_info[0]}")
        print(f"✅ 사용자: {db_info[1]}")
        
        # 5. 테이블 생성/삭제 테스트
        print("\n🛠️ 테이블 작업 테스트...")
        
        # 테스트 테이블 생성
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS airiss_test_simple (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 테스트 테이블 생성 성공")
        
        # 데이터 삽입
        cursor.execute("""
            INSERT INTO airiss_test_simple (name) VALUES (%s)
        """, ('AIRISS 테스트',))
        print("✅ 데이터 삽입 성공")
        
        # 데이터 조회
        cursor.execute("SELECT COUNT(*) FROM airiss_test_simple;")
        count = cursor.fetchone()[0]
        print(f"✅ 테이블 데이터 수: {count}")
        
        # 변경사항 커밋
        conn.commit()
        
        # 테스트 테이블 삭제
        cursor.execute("DROP TABLE IF EXISTS airiss_test_simple;")
        conn.commit()
        print("✅ 테스트 테이블 삭제 성공")
        
        # 6. 연결 종료
        cursor.close()
        conn.close()
        print("✅ 연결 정상 종료")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def main():
    """메인 실행"""
    success = test_psycopg2_only()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 네온 DB 연결 테스트 성공!")
        print("✅ AIRISS 프로젝트에서 네온 DB를 사용할 수 있습니다.")
    else:
        print("❌ 네온 DB 연결 테스트 실패")
        print("💡 문제 해결:")
        print("  1. .env 파일의 POSTGRES_DATABASE_URL 확인")
        print("  2. 네온 DB 계정 상태 확인")
        print("  3. 인터넷 연결 상태 확인")
    
    print(f"\n📅 테스트 시간: {datetime.now()}")
    return success

if __name__ == "__main__":
    main()
    input("\n아무 키나 눌러 종료...")