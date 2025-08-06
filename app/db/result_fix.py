"""
데이터베이스 results 테이블 조회 함수 추가
"""

from sqlalchemy import text
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def get_results_by_job_id(db_service, job_id: str) -> List[Dict[str, Any]]:
    """job_id로 results 테이블에서 결과 조회"""
    db = db_service.get_session()
    try:
        sql = """
            SELECT * FROM results 
            WHERE job_id = :job_id 
            ORDER BY created_at
        """
        results = db.execute(text(sql), {'job_id': job_id}).fetchall()
        
        result_list = []
        for row in results:
            result_dict = dict(row._mapping)
            
            # datetime 객체를 문자열로 변환
            for key, value in result_dict.items():
                if isinstance(value, datetime):
                    result_dict[key] = value.isoformat()
            
            # JSON 컬럼 파싱
            for col in ['dimension_scores', 'result_data']:
                val = result_dict.get(col)
                if val and isinstance(val, str):
                    try:
                        import json
                        result_dict[col] = json.loads(val)
                    except:
                        pass
            
            result_list.append(result_dict)
        
        logger.info(f"✅ Results 테이블 조회 성공: {len(result_list)} 개")
        return result_list
        
    except Exception as e:
        logger.error(f"❌ Results 테이블 조회 오류: {e}")
        raise
    finally:
        db.close()


def patch_db_service(db_service):
    """DB 서비스에 get_results_by_job_id 메서드 추가"""
    db_service.get_results_by_job_id = lambda job_id: get_results_by_job_id(db_service, job_id)
    logger.info("✅ DB 서비스에 get_results_by_job_id 메서드 추가 완료")