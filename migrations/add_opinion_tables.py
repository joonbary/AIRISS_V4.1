"""
평가의견 분석 테이블 추가 마이그레이션
Add opinion analysis tables migration
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect
from app.db.database import DATABASE_URL
from app.models.opinion_result import OpinionResult, OpinionKeyword
from app.models import Base

def add_opinion_tables():
    """평가의견 분석 관련 테이블 생성"""
    
    # 데이터베이스 엔진 생성
    engine = create_engine(DATABASE_URL)
    
    # 인스펙터로 기존 테이블 확인
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print("Existing tables:", existing_tables)
    
    # OpinionResult 테이블이 없으면 생성
    if 'opinion_results' not in existing_tables:
        OpinionResult.__table__.create(engine)
        print("[SUCCESS] Created opinion_results table")
    else:
        print("[WARNING] opinion_results table already exists")
    
    # OpinionKeyword 테이블이 없으면 생성
    if 'opinion_keywords' not in existing_tables:
        OpinionKeyword.__table__.create(engine)
        print("[SUCCESS] Created opinion_keywords table")
    else:
        print("[WARNING] opinion_keywords table already exists")
    
    # 생성된 테이블 확인
    inspector = inspect(engine)
    new_tables = inspector.get_table_names()
    print("\nTables after migration:", new_tables)
    
    # 컬럼 정보 출력
    if 'opinion_results' in new_tables:
        columns = inspector.get_columns('opinion_results')
        print("\nopinion_results columns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    
    if 'opinion_keywords' in new_tables:
        columns = inspector.get_columns('opinion_keywords')
        print("\nopinion_keywords columns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

if __name__ == "__main__":
    print("Starting opinion tables migration...")
    add_opinion_tables()
    print("\nMigration completed!")