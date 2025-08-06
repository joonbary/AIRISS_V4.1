"""
NeonDB 연결 테스트 스크립트
"""
import os
import sys
from dotenv import load_dotenv

# Windows에서 UTF-8 인코딩 설정
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 환경 변수 로드
load_dotenv()

# DATABASE_URL 확인
database_url = os.getenv("DATABASE_URL")
use_database = os.getenv("USE_DATABASE", "false").lower() == "true"

print("=== NeonDB 연결 설정 확인 ===")
print(f"USE_DATABASE: {use_database}")
print(f"DATABASE_URL: {database_url[:50]}..." if database_url else "DATABASE_URL: Not set")

if not use_database:
    print("\n⚠️  USE_DATABASE가 false로 설정되어 있습니다.")
    print("   외부 DB를 사용하려면 .env 파일에서 USE_DATABASE=true로 설정하세요.")
    sys.exit(0)

if not database_url:
    print("\n❌ DATABASE_URL이 설정되지 않았습니다.")
    sys.exit(1)

# 데이터베이스 연결 테스트
try:
    from sqlalchemy import create_engine, text
    
    print("\n데이터베이스 연결 테스트 중...")
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ NeonDB 연결 성공!")
        
        # 테이블 목록 확인
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        
        tables = [row[0] for row in result]
        print(f"\n현재 테이블 목록 ({len(tables)}개):")
        for table in tables:
            print(f"  - {table}")
            
        # analysis_results 관련 테이블 확인
        analysis_tables = [t for t in tables if 'analysis' in t or 'result' in t]
        if analysis_tables:
            print(f"\n분석 결과 관련 테이블:")
            for table in analysis_tables:
                print(f"  - {table}")
        else:
            print("\n⚠️  분석 결과 테이블이 없습니다. 마이그레이션이 필요할 수 있습니다.")
        
except ImportError:
    print("\n❌ sqlalchemy가 설치되지 않았습니다.")
    print("   pip install sqlalchemy psycopg2-binary 를 실행하세요.")
except Exception as e:
    print(f"\n❌ 데이터베이스 연결 실패: {str(e)}")
    
print("\n=== 테스트 완료 ===")