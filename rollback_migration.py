"""
마이그레이션 롤백 스크립트
"""
import asyncio
from sqlalchemy import text
from app.db import db_service

async def rollback_migration():
    """마이그레이션 롤백"""
    print("=== 마이그레이션 롤백 시작 ===")
    
    db = db_service.get_session()
    try:
        # 뷰 삭제
        print("뷰 삭제 중...")
        db.execute(text("DROP VIEW IF EXISTS results_view"))
        db.execute(text("DROP VIEW IF EXISTS analysis_results_view"))
        
        # 테이블 삭제
        print("테이블 삭제 중...")
        db.execute(text("DROP TABLE IF EXISTS analysis_results_v2"))
        
        db.commit()
        print("[SUCCESS] 롤백 완료")
        
    except Exception as e:
        print(f"[FAIL] 롤백 실패: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(rollback_migration())