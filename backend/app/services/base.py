"""
Base Service
서비스 클래스의 기본 클래스
"""

from typing import Optional
from sqlalchemy.orm import Session
import logging


class BaseService:
    """서비스 기본 클래스"""
    
    def __init__(self, db: Session, logger: Optional[logging.Logger] = None):
        self.db = db
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    def commit(self):
        """트랜잭션 커밋"""
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Commit failed: {e}")
            raise
    
    def rollback(self):
        """트랜잭션 롤백"""
        self.db.rollback()