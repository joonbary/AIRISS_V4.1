"""
간단한 평가의견 분석 API (테스트용)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
import logging

from app.db.database import get_db
from app.schemas.opinion import OpinionUploadRequest

router = APIRouter(tags=["Opinion Test"])
logger = logging.getLogger(__name__)


@router.post("/test")
def test_opinion_analysis(
    request: OpinionUploadRequest,
    db: Session = Depends(get_db)
):
    """
    간단한 동기식 테스트 엔드포인트
    """
    try:
        logger.info(f"Test analysis request for UID: {request.uid}")
        
        # 단순한 응답 반환
        return {
            "uid": request.uid,
            "summary": "테스트 분석 완료",
            "strengths": ["성실성", "책임감"],
            "weaknesses": ["혁신성"],
            "text_score": 75.0,
            "hybrid_score": 76.5,
            "dimension_scores": {
                "leadership": 70,
                "collaboration": 75,
                "problem_solving": 72,
                "innovation": 65,
                "communication": 73,
                "expertise": 71,
                "execution": 74,
                "growth": 68
            }
        }
    except Exception as e:
        logger.error(f"Test analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))