"""
Database Service Wrapper
기존 코드와의 호환성을 위한 래퍼
새로운 코드는 app.db.repositories를 직접 사용하세요
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.db import get_db, AnalysisRepository, FileRepository, UserRepository

logger = logging.getLogger(__name__)


class DatabaseService:
    """기존 DatabaseService 호환성 래퍼"""
    
    def __init__(self):
        logger.warning("Deprecated: DatabaseService를 사용하지 마세요. Repository 패턴을 사용하세요.")
    
    def get_session(self) -> Session:
        """새 DB 세션 생성"""
        return next(get_db())
    
    async def save_file(self, file_data: Dict[str, Any]) -> str:
        """파일 정보 저장 (호환성)"""
        db = self.get_session()
        try:
            repo = FileRepository(db)
            return repo.save_file(file_data)
        finally:
            db.close()
    
    async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """파일 정보 조회 (호환성)"""
        db = self.get_session()
        try:
            repo = FileRepository(db)
            return repo.get_file(file_id)
        finally:
            db.close()
    
    async def create_analysis_job(self, job_data: Dict[str, Any]) -> str:
        """분석 작업 생성 (호환성)"""
        db = self.get_session()
        try:
            repo = AnalysisRepository(db)
            return repo.create_job(job_data)
        finally:
            db.close()
    
    async def get_analysis_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """분석 작업 조회 (호환성)"""
        db = self.get_session()
        try:
            repo = AnalysisRepository(db)
            return repo.get_job(job_id)
        finally:
            db.close()
    
    async def update_analysis_job(self, job_id: str, update_data: Dict[str, Any]) -> bool:
        """분석 작업 업데이트 (호환성)"""
        db = self.get_session()
        try:
            repo = AnalysisRepository(db)
            return repo.update_job(job_id, update_data)
        finally:
            db.close()
    
    async def save_analysis_result(self, result_data: Dict[str, Any]) -> str:
        """분석 결과 저장 (호환성)"""
        db = self.get_session()
        try:
            repo = AnalysisRepository(db)
            return repo.save_result(result_data)
        finally:
            db.close()
    
    async def get_analysis_results(self, job_id: str = None, file_id: str = None, 
                                  uid: str = None) -> List[Dict[str, Any]]:
        """분석 결과 조회 (호환성)"""
        db = self.get_session()
        try:
            repo = AnalysisRepository(db)
            return repo.get_results(job_id, file_id, uid)
        finally:
            db.close()
    
    async def list_files(self, user_id: Optional[str] = None, 
                        session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """파일 목록 조회 (호환성)"""
        db = self.get_session()
        try:
            repo = FileRepository(db)
            return repo.list_files(user_id, session_id)
        finally:
            db.close()
    
    async def init_database(self):
        """데이터베이스 초기화 (호환성)"""
        from app.db import init_db
        init_db()


# 기존 코드와의 호환성을 위한 전역 인스턴스
db_service = DatabaseService()

# Export
__all__ = ['db_service', 'DatabaseService']
