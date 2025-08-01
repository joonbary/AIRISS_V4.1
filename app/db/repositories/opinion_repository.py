"""
평가의견 데이터베이스 리포지토리
Opinion database repository
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.opinion_result import OpinionResult, OpinionKeyword


class OpinionRepository:
    """평가의견 리포지토리"""
    
    def __init__(self, db: Session):
        """
        리포지토리 초기화
        
        Args:
            db: 데이터베이스 세션
        """
        self.db = db
    
    def get_by_uid(self, uid: str) -> Optional[OpinionResult]:
        """
        UID로 평가의견 결과 조회
        
        Args:
            uid: 직원 UID
            
        Returns:
            평가의견 결과 또는 None
        """
        return self.db.query(OpinionResult).filter(
            OpinionResult.uid == uid
        ).first()
    
    def get_by_id(self, opinion_id: str) -> Optional[OpinionResult]:
        """
        ID로 평가의견 결과 조회
        
        Args:
            opinion_id: 평가의견 ID
            
        Returns:
            평가의견 결과 또는 None
        """
        return self.db.query(OpinionResult).filter(
            OpinionResult.id == opinion_id
        ).first()
    
    def get_multiple_by_uids(self, uids: List[str]) -> List[OpinionResult]:
        """
        여러 UID로 평가의견 결과 조회
        
        Args:
            uids: UID 리스트
            
        Returns:
            평가의견 결과 리스트
        """
        return self.db.query(OpinionResult).filter(
            OpinionResult.uid.in_(uids)
        ).all()
    
    def get_keywords_by_opinion_id(self, opinion_id: str) -> List[OpinionKeyword]:
        """
        평가의견 ID로 키워드 조회
        
        Args:
            opinion_id: 평가의견 ID
            
        Returns:
            키워드 리스트
        """
        return self.db.query(OpinionKeyword).filter(
            OpinionKeyword.opinion_result_id == opinion_id
        ).all()
    
    def get_top_keywords(
        self, 
        keyword_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, any]]:
        """
        인기 키워드 조회
        
        Args:
            keyword_type: 키워드 타입 (strength/weakness)
            limit: 조회 개수
            
        Returns:
            키워드 통계 리스트
        """
        query = self.db.query(
            OpinionKeyword.keyword,
            OpinionKeyword.keyword_type,
            self.db.query(OpinionKeyword).filter(
                OpinionKeyword.keyword == OpinionKeyword.keyword
            ).count().label('count')
        )
        
        if keyword_type:
            query = query.filter(OpinionKeyword.keyword_type == keyword_type)
        
        results = query.group_by(
            OpinionKeyword.keyword,
            OpinionKeyword.keyword_type
        ).order_by('count DESC').limit(limit).all()
        
        return [
            {
                'keyword': r.keyword,
                'type': r.keyword_type,
                'count': r.count
            }
            for r in results
        ]
    
    def update_opinion_result(
        self,
        uid: str,
        update_data: Dict[str, any]
    ) -> Optional[OpinionResult]:
        """
        평가의견 결과 업데이트
        
        Args:
            uid: 직원 UID
            update_data: 업데이트할 데이터
            
        Returns:
            업데이트된 결과 또는 None
        """
        opinion_result = self.get_by_uid(uid)
        
        if not opinion_result:
            return None
        
        for key, value in update_data.items():
            if hasattr(opinion_result, key):
                setattr(opinion_result, key, value)
        
        self.db.commit()
        self.db.refresh(opinion_result)
        
        return opinion_result
    
    def delete_by_uid(self, uid: str) -> bool:
        """
        UID로 평가의견 결과 삭제
        
        Args:
            uid: 직원 UID
            
        Returns:
            삭제 성공 여부
        """
        opinion_result = self.get_by_uid(uid)
        
        if not opinion_result:
            return False
        
        # 관련 키워드도 삭제
        self.db.query(OpinionKeyword).filter(
            OpinionKeyword.opinion_result_id == opinion_result.id
        ).delete()
        
        self.db.delete(opinion_result)
        self.db.commit()
        
        return True
    
    def get_statistics(self) -> Dict[str, any]:
        """
        평가의견 분석 통계 조회
        
        Returns:
            통계 정보
        """
        total_count = self.db.query(OpinionResult).count()
        
        avg_scores = self.db.query(
            self.db.func.avg(OpinionResult.text_score).label('avg_text_score'),
            self.db.func.avg(OpinionResult.hybrid_score).label('avg_hybrid_score'),
            self.db.func.avg(OpinionResult.sentiment_score).label('avg_sentiment'),
            self.db.func.avg(OpinionResult.confidence).label('avg_confidence')
        ).first()
        
        return {
            'total_analyzed': total_count,
            'average_text_score': round(avg_scores.avg_text_score or 0, 2),
            'average_hybrid_score': round(avg_scores.avg_hybrid_score or 0, 2),
            'average_sentiment': round(avg_scores.avg_sentiment or 0, 2),
            'average_confidence': round(avg_scores.avg_confidence or 0, 2)
        }