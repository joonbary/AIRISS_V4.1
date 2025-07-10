# -*- coding: utf-8 -*-
"""
AIRISS 네온 DB 연결 테스트 스크립트
.env 파일 설정을 확인하고 데이터베이스 연결을 테스트합니다.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import psycopg2
from datetime import datetime

def load_environment():
    """환경변수 로드"""
    print("🔧 환경변수 로드 중...")
    
    # .env 파일 로드
    env_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ .env 파일 로드 완료: {env_path}")
    else:
        print(f"⚠️ .env 파일 없음: {env_path}")
        return False
    
    # 필수 환경변수 확인
    required_vars = ['DATABASE_TYPE', 'DATABASE_URL', 'POSTGRES_DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'password' in var.lower() or 'url' in var.lower():
                masked_value = value.split('@')[0] + '@***' if '@' in value else value[:10] + '***'
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"  ❌ {var}: 없음")
    
    if missing_vars:
        print(f"⚠️ 누락된 환경변수: {missing_vars}")
        return False
    
    return True

def test_basic_connection():
    """기본 psycopg2를 사용한 연결 테스트"""
    print("\n🔌 기본 PostgreSQL 연결 테스트...")
    
    try:
        # 환경변수에서 URL 파싱
        postgres_url = os.getenv('POSTGRES_DATABASE_URL')
        if not postgres_url:
            print("❌ POSTGRES_DATABASE_URL 환경변수 없음")
            return False
        
        # URL에서 연결 정보 추출
        if postgres_url.startswith('postgresql://'):
            url_parts = postgres_url.replace('postgresql://', '').split('@')
            if len(url_parts) != 2:
                print("❌ PostgreSQL URL 형식 오류")
                return False
            
            user_pass = url_parts[0].split(':')
            host_db = url_parts[1].split('/')
            
            if len(user_pass) != 2 or len(host_db) < 2:
                print("❌ PostgreSQL URL 파싱 오류")
                return False
            
            user = user_pass[0]
            password = user_pass[1]
            host_port = host_db[0]
            database = host_db[1].split('?')[0]  # 쿼리 파라미터 제거
            
            if ':' in host_port:
                host, port = host_port.split(':')
            else:
                host = host_port
                port = 5432
            
            print(f"  📡 호스트: {host}")
            print(f"  🔌 포트: {port}")
            print(f"  🗄️ 데이터베이스: {database}")
            print(f"  👤 사용자: {user}")
        
        # psycopg2로 직접 연결
        conn = psycopg2.connect(postgres_url)
        cursor = conn.cursor()
        
        # 기본 쿼리 테스트
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL 버전: {version[0][:50]}...")
        
        # 간단한 테스트 쿼리
        cursor.execute("SELECT current_timestamp;")
        timestamp = cursor.fetchone()
        print(f"✅ 서버 시간: {timestamp[0]}")
        
        cursor.close()
        conn.close()
        
        print("✅ 기본 PostgreSQL 연결 성공!")
        return True
        
    except Exception as e:
        print(f"❌ 기본 PostgreSQL 연결 실패: {e}")
        return False

def test_sqlalchemy_connection():
    """SQLAlchemy를 사용한 연결 테스트"""
    print("\n🔗 SQLAlchemy 연결 테스트...")
    
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL 환경변수 없음")
            return False
        
        print(f"  🔗 URL: {database_url.split('@')[0]}@***")
        
        # SQLAlchemy 엔진 생성
        engine = create_engine(
            database_url,
            echo=False,
            connect_args={
                "sslmode": "require",
                "connect_timeout": 30,
            }
        )
        
        # 연결 테스트
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                print("✅ SQLAlchemy 연결 테스트 성공!")
                
                # 추가 테스트
                result = connection.execute(text("SELECT current_database(), current_user"))
                db_info = result.fetchone()
                print(f"  🗄️ 현재 DB: {db_info[0]}")
                print(f"  👤 현재 사용자: {db_info[1]}")
                
                return True
            else:
                print("❌ SQLAlchemy 테스트 쿼리 결과 오류")
                return False
        
    except Exception as e:
        print(f"❌ SQLAlchemy 연결 실패: {e}")
        return False

def test_table_operations():
    """기본 테이블 작업 테스트"""
    print("\n📋 테이블 작업 테스트...")
    
    try:
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # 테스트 테이블 생성
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS airiss_test (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            connection.commit()
            print("✅ 테스트 테이블 생성 성공")
            
            # 데이터 삽입
            connection.execute(text("""
                INSERT INTO airiss_test (name) VALUES ('Test Entry')
            """))
            connection.commit()
            print("✅ 데이터 삽입 성공")
            
            # 데이터 조회
            result = connection.execute(text("SELECT COUNT(*) FROM airiss_test"))
            count = result.fetchone()[0]
            print(f"✅ 테이블 데이터 수: {count}")
            
            # 테스트 테이블 삭제
            connection.execute(text("DROP TABLE IF EXISTS airiss_test"))
            connection.commit()
            print("✅ 테스트 테이블 삭제 성공")
            
            return True
            
    except Exception as e:
        print(f"❌ 테이블 작업 테스트 실패: {e}")
        return False

def check_dependencies():
    """필수 패키지 확인"""
    print("\n📦 필수 패키지 확인...")
    
    required_packages = {
        'psycopg2': 'psycopg2-binary',
        'sqlalchemy': 'SQLAlchemy',
        'python-dotenv': 'python-dotenv'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {package}: 설치됨")
        except ImportError:
            print(f"  ❌ {package}: 없음")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n💾 설치 필요한 패키지:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def generate_diagnosis_report():
    """진단 보고서 생성"""
    print("\n📊 진단 보고서 생성 중...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'environment_loaded': False,
        'dependencies_ok': False,
        'basic_connection': False,
        'sqlalchemy_connection': False,
        'table_operations': False
    }
    
    # 테스트 실행
    report['dependencies_ok'] = check_dependencies()
    if not report['dependencies_ok']:
        return report
    
    report['environment_loaded'] = load_environment()
    if not report['environment_loaded']:
        return report
    
    report['basic_connection'] = test_basic_connection()
    report['sqlalchemy_connection'] = test_sqlalchemy_connection()
    
    if report['sqlalchemy_connection']:
        report['table_operations'] = test_table_operations()
    
    return report

def main():
    """메인 실행 함수"""
    print("🚀 AIRISS 네온 DB 연결 진단 시작")
    print("=" * 50)
    
    # 진단 실행
    report = generate_diagnosis_report()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("📋 진단 결과 요약")
    print("=" * 50)
    
    tests = [
        ('패키지 설치', report['dependencies_ok']),
        ('환경변수 로드', report['environment_loaded']),
        ('기본 PostgreSQL 연결', report['basic_connection']),
        ('SQLAlchemy 연결', report['sqlalchemy_connection']),
        ('테이블 작업', report['table_operations'])
    ]
    
    for test_name, result in tests:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"  {test_name}: {status}")
    
    # 전체 결과
    all_passed = all(report.values())
    if all_passed:
        print("\n🎉 모든 테스트 통과! 네온 DB 연결이 정상입니다.")
    else:
        print("\n⚠️ 일부 테스트 실패. 위의 오류 메시지를 확인하세요.")
        
        # 권장사항
        print("\n💡 문제 해결 권장사항:")
        if not report['dependencies_ok']:
            print("  1. 필수 패키지를 설치하세요")
        if not report['environment_loaded']:
            print("  2. .env 파일의 환경변수를 확인하세요")
        if not report['basic_connection']:
            print("  3. 네온 DB 연결 정보가 정확한지 확인하세요")
        if not report['sqlalchemy_connection']:
            print("  4. DATABASE_URL 형식을 확인하세요")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)