"""
평가의견 분석 API 엔드포인트
Opinion analysis API endpoints
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import pandas as pd
import json
import io

from app.db.database import get_db
from app.schemas.opinion import (
    OpinionUploadRequest,
    OpinionBatchUploadRequest,
    OpinionAnalysisResult,
    OpinionAnalysisResponse,
    HybridScoreConfig
)
from app.services.opinion_analysis_service import OpinionAnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Opinion Analysis"]
)


@router.post("/analyze", response_model=OpinionAnalysisResponse)
async def analyze_opinion(
    request: OpinionUploadRequest,
    db: Session = Depends(get_db)
):
    """
    단일 직원 평가의견 분석
    
    - **uid**: 직원 고유 ID
    - **opinions**: 연도별 평가의견 딕셔너리
    """
    try:
        service = OpinionAnalysisService(db)
        result = await service.analyze_opinion(request)
        
        return OpinionAnalysisResponse(
            success=True,
            result=result
        )
    except Exception as e:
        logger.error(f"Opinion analysis failed: {str(e)}")
        return OpinionAnalysisResponse(
            success=False,
            message=str(e)
        )


@router.post("/analyze/batch", response_model=List[OpinionAnalysisResponse])
async def analyze_opinions_batch(
    request: OpinionBatchUploadRequest,
    db: Session = Depends(get_db)
):
    """
    다수 직원 평가의견 일괄 분석
    
    - **data**: 분석할 직원 리스트
    - **force_update**: 기존 분석 결과 덮어쓰기 여부
    """
    try:
        service = OpinionAnalysisService(db)
        results = await service.analyze_batch(request.data)
        
        return [
            OpinionAnalysisResponse(success=True, result=result)
            for result in results
        ]
    except Exception as e:
        logger.error(f"Batch opinion analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/excel")
async def upload_opinion_excel(
    file: UploadFile = File(...),
    sheet_name: Optional[str] = Form(None),
    uid_column: str = Form("UID"),
    db: Session = Depends(get_db)
):
    """
    엑셀 파일로 평가의견 업로드 및 분석
    
    엑셀 형식:
    - UID 컬럼 필수
    - 연도별 평가의견 컬럼 (예: 의견_2023, 의견_2022 등)
    """
    try:
        # 파일 읽기
        contents = await file.read()
        
        # 파일 확장자 확인
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="Only Excel files (.xlsx, .xls) are supported"
            )
        
        # pandas로 읽기
        df = pd.read_excel(
            io.BytesIO(contents),
            sheet_name=sheet_name or 0
        )
        
        # UID 컬럼 확인
        if uid_column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"UID column '{uid_column}' not found in Excel file"
            )
        
        # 평가의견 컬럼 찾기
        opinion_columns = [col for col in df.columns if '의견' in col or 'opinion' in col.lower()]
        
        if not opinion_columns:
            raise HTTPException(
                status_code=400,
                detail="No opinion columns found. Column names should contain '의견' or 'opinion'"
            )
        
        # 데이터 변환
        requests = []
        for _, row in df.iterrows():
            uid = str(row[uid_column])
            opinions = {}
            
            for col in opinion_columns:
                # 연도 추출 (예: 의견_2023 -> 2023)
                import re
                year_match = re.search(r'(\d{4})', col)
                if year_match:
                    year = year_match.group(1)
                    value = row[col]
                    # NaN 처리
                    if pd.notna(value):
                        opinions[year] = str(value)
                    else:
                        opinions[year] = None
            
            if opinions:  # 최소 하나의 평가의견이 있는 경우만
                requests.append(
                    OpinionUploadRequest(uid=uid, opinions=opinions)
                )
        
        if not requests:
            raise HTTPException(
                status_code=400,
                detail="No valid opinion data found in Excel file"
            )
        
        # 분석 실행
        service = OpinionAnalysisService(db)
        results = await service.analyze_batch(requests)
        
        return {
            "success": True,
            "message": f"Analyzed {len(results)} employees",
            "total_uploaded": len(requests),
            "successfully_analyzed": len(results),
            "failed": len(requests) - len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Excel upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{uid}", response_model=OpinionAnalysisResult)
async def get_opinion_analysis(
    uid: str,
    db: Session = Depends(get_db)
):
    """
    특정 직원의 평가의견 분석 결과 조회
    """
    from app.db.repositories.opinion_repository import OpinionRepository
    
    repo = OpinionRepository(db)
    result = repo.get_by_uid(uid)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Opinion analysis not found for UID: {uid}"
        )
    
    # OpinionResult를 OpinionAnalysisResult로 변환
    from app.schemas.opinion import DimensionScore
    
    return OpinionAnalysisResult(
        uid=result.uid,
        summary=result.summary,
        strengths=result.strengths,
        weaknesses=result.weaknesses,
        text_score=result.text_score,
        sentiment_score=result.sentiment_score,
        specificity_score=result.specificity_score,
        consistency_score=result.consistency_score,
        dimension_scores=DimensionScore(**result.dimension_scores),
        hybrid_score=result.hybrid_score,
        confidence=result.confidence,
        years_analyzed=result.years_analyzed,
        analyzed_at=result.analyzed_at,
        processing_time=result.processing_time
    )


@router.get("/statistics/summary")
async def get_opinion_statistics(db: Session = Depends(get_db)):
    """
    전체 평가의견 분석 통계 조회
    """
    from app.db.repositories.opinion_repository import OpinionRepository
    
    repo = OpinionRepository(db)
    stats = repo.get_statistics()
    
    # 인기 키워드 추가
    top_strengths = repo.get_top_keywords(keyword_type="strength", limit=5)
    top_weaknesses = repo.get_top_keywords(keyword_type="weakness", limit=5)
    
    stats.update({
        "top_strengths": top_strengths,
        "top_weaknesses": top_weaknesses
    })
    
    return stats


@router.delete("/{uid}")
async def delete_opinion_analysis(
    uid: str,
    db: Session = Depends(get_db)
):
    """
    특정 직원의 평가의견 분석 결과 삭제
    """
    from app.db.repositories.opinion_repository import OpinionRepository
    
    repo = OpinionRepository(db)
    success = repo.delete_by_uid(uid)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Opinion analysis not found for UID: {uid}"
        )
    
    return {"success": True, "message": f"Opinion analysis deleted for UID: {uid}"}


@router.post("/recalculate/{uid}")
async def recalculate_hybrid_score(
    uid: str,
    config: Optional[HybridScoreConfig] = None,
    db: Session = Depends(get_db)
):
    """
    특정 직원의 하이브리드 점수 재계산
    
    정량 점수가 업데이트된 경우 하이브리드 점수를 재계산합니다.
    """
    from app.db.repositories.opinion_repository import OpinionRepository
    from app.models.employee import EmployeeResult
    
    # 기존 분석 결과 조회
    repo = OpinionRepository(db)
    opinion_result = repo.get_by_uid(uid)
    
    if not opinion_result:
        raise HTTPException(
            status_code=404,
            detail=f"Opinion analysis not found for UID: {uid}"
        )
    
    # 직원 정량 점수 조회
    employee_result = db.query(EmployeeResult).filter(
        EmployeeResult.uid == uid
    ).first()
    
    if not employee_result:
        raise HTTPException(
            status_code=404,
            detail=f"Employee result not found for UID: {uid}"
        )
    
    # 하이브리드 점수 재계산
    config = config or HybridScoreConfig()
    
    new_hybrid_score = (
        employee_result.overall_score * config.quantitative_weight +
        opinion_result.text_score * config.text_weight
    )
    
    # 업데이트
    opinion_result.hybrid_score = round(new_hybrid_score, 2)
    employee_result.overall_score = opinion_result.hybrid_score
    
    db.commit()
    
    return {
        "success": True,
        "uid": uid,
        "quantitative_score": employee_result.overall_score,
        "text_score": opinion_result.text_score,
        "new_hybrid_score": opinion_result.hybrid_score,
        "weights": {
            "quantitative": config.quantitative_weight,
            "text": config.text_weight
        }
    }