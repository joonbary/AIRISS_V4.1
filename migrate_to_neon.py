"""
SQLite에서 Neon DB로 데이터 마이그레이션 스크립트
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_to_neon():
    """SQLite에서 Neon DB로 데이터 마이그레이션"""
    
    # 1. 환경 변수 로드
    from dotenv import load_dotenv
    load_dotenv()
    
    # SQLite 연결
    sqlite_url = "sqlite:///./airiss.db"
    sqlite_engine = create_engine(sqlite_url)
    
    # Neon DB 연결 (환경 변수에서)
    neon_url = os.getenv("DATABASE_URL")
    if not neon_url or "postgresql" not in neon_url:
        logger.error("Neon DB URL이 설정되지 않았습니다. .env 파일을 확인하세요.")
        return False
    
    try:
        neon_engine = create_engine(neon_url)
        
        # 연결 테스트
        with neon_engine.connect() as conn:
            logger.info("✅ Neon DB 연결 성공!")
    except Exception as e:
        logger.error(f"❌ Neon DB 연결 실패: {e}")
        return False
    
    # 2. 테이블 목록
    tables_to_migrate = ['users', 'jobs', 'analysis_results', 'files']
    
    # 3. 각 테이블 마이그레이션
    for table_name in tables_to_migrate:
        try:
            # SQLite에서 데이터 읽기
            df = pd.read_sql_table(table_name, sqlite_engine)
            
            if df.empty:
                logger.info(f"📋 {table_name} 테이블이 비어있습니다.")
                continue
            
            # Neon DB로 데이터 쓰기
            df.to_sql(table_name, neon_engine, if_exists='append', index=False)
            logger.info(f"✅ {table_name} 테이블 마이그레이션 완료: {len(df)}개 레코드")
            
        except Exception as e:
            logger.error(f"❌ {table_name} 테이블 마이그레이션 실패: {e}")
    
    logger.info("🎉 마이그레이션 완료!")
    return True

def test_neon_connection():
    """Neon DB 연결 테스트"""
    from dotenv import load_dotenv
    load_dotenv()
    
    neon_url = os.getenv("DATABASE_URL")
    if not neon_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return
    
    # URL에서 패스워드 부분 숨기기
    display_url = neon_url.split('@')[0].split(':')[0] + ":****@" + neon_url.split('@')[1]
    print(f"🔗 연결 시도: {display_url}")
    
    try:
        engine = create_engine(neon_url)
        with engine.connect() as conn:
            result = conn.execute("SELECT version()")
            version = result.fetchone()[0]
            print(f"✅ Neon DB 연결 성공!")
            print(f"📊 PostgreSQL 버전: {version}")
            
            # 테이블 목록 확인
            result = conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in result]
            print(f"📋 현재 테이블: {tables}")
            
    except Exception as e:
        print(f"❌ 연결 실패: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_neon_connection()
    else:
        migrate_to_neon()