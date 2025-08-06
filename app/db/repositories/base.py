"""
Base Repository Pattern
모든 리포지토리의 기본 클래스
"""

from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from abc import ABC, abstractmethod

Base = declarative_base()
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType], ABC):
    """리포지토리 패턴 기본 클래스"""
    
    def __init__(self, model: Type[ModelType], db_session: Session):
        self.model = model
        self.db = db_session
    
    def get(self, id: int) -> Optional[ModelType]:
        """ID로 단일 객체 조회"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """전체 목록 조회"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, **kwargs) -> ModelType:
        """새 객체 생성"""
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """객체 업데이트"""
        db_obj = self.get(id)
        if db_obj:
            for key, value in kwargs.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        """객체 삭제"""
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
    
    def commit(self):
        """변경사항 커밋"""
        self.db.commit()
    
    def rollback(self):
        """변경사항 롤백"""
        self.db.rollback()