"""
Neon DB에 누락된 컬럼 추가 스크립트
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_columns():
    """누락된 컬럼 추가"""
    
    # 환경 변수 로드
    load_dotenv()
    
    # Neon DB 연결
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL이 설정되지 않았습니다.")
        return False
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # 트랜잭션 시작
            trans = conn.begin()
            
            try:
                # jobs 테이블에 results_data 컬럼 추가
                logger.info("jobs 테이블에 results_data 컬럼 추가 중...")
                conn.execute(text("""
                    ALTER TABLE jobs 
                    ADD COLUMN IF NOT EXISTS results_data TEXT;
                """))
                
                # 다른 누락된 컬럼들도 확인하고 추가
                columns_to_check = [
                    ("jobs", "job_data", "TEXT"),
                    ("jobs", "results_data", "TEXT"),
                    ("jobs", "enable_ai_feedback", "BOOLEAN DEFAULT FALSE"),
                    ("jobs", "openai_model", "VARCHAR(100)"),
                    ("jobs", "max_tokens", "INTEGER"),
                    ("jobs", "progress", "FLOAT DEFAULT 0.0"),
                    ("jobs", "total_records", "INTEGER DEFAULT 0"),
                    ("jobs", "processed_records", "INTEGER DEFAULT 0"),
                    ("jobs", "failed_records", "INTEGER DEFAULT 0"),
                    ("jobs", "error", "TEXT")
                ]
                
                for table, column, data_type in columns_to_check:
                    try:
                        conn.execute(text(f"""
                            ALTER TABLE {table} 
                            ADD COLUMN IF NOT EXISTS {column} {data_type};
                        """))
                        logger.info(f"✅ {table}.{column} 컬럼 확인/추가 완료")
                    except Exception as e:
                        # 컬럼이 이미 존재하는 경우 무시
                        if "already exists" in str(e).lower():
                            logger.info(f"ℹ️ {table}.{column} 컬럼은 이미 존재합니다")
                        else:
                            logger.error(f"❌ {table}.{column} 추가 실패: {e}")
                
                # 변경사항 커밋
                trans.commit()
                logger.info("✅ 모든 컬럼 추가 완료!")
                
                # 현재 jobs 테이블 구조 확인
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'jobs'
                    ORDER BY ordinal_position;
                """))
                
                logger.info("\n📋 jobs 테이블 현재 구조:")
                for row in result:
                    logger.info(f"  - {row[0]}: {row[1]}")
                
                return True
                
            except Exception as e:
                trans.rollback()
                logger.error(f"트랜잭션 실패: {e}")
                return False
                
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        return False

if __name__ == "__main__":
    add_missing_columns()