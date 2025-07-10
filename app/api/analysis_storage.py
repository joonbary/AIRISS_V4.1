# app/api/analysis_storage.py
# 분석 결과 저장 및 조회 API 엔드포인트

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.services.analysis_storage_service import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/analysis-storage",
    tags=["analysis-storage"]
)

@router.post("/save")
async def save_analysis_result(analysis_data: Dict[str, Any]):
    """
    분석 결과 저장
    
    Args:
        analysis_data: 분석 결과 데이터
        
    Returns:
        저장된 분석 결과 ID
    """
    try:
        analysis_id = storage_service.save_analysis_result(analysis_data)
        return {
            "success": True,
            "analysis_id": analysis_id,
            "message": "분석 결과가 성공적으로 저장되었습니다."
        }
    except Exception as e:
        logger.error(f"분석 결과 저장 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results")
async def get_analysis_results(
    file_id: Optional[str] = Query(None, description="파일 ID로 필터링"),
    uid: Optional[str] = Query(None, description="사용자 ID로 필터링"),
    limit: int = Query(100, description="결과 수 제한"),
    offset: int = Query(0, description="페이지네이션 오프셋")
):
    """
    분석 결과 조회
    
    Args:
        file_id: 파일 ID 필터
        uid: 사용자 ID 필터
        limit: 결과 수 제한
        offset: 페이지네이션 오프셋
        
    Returns:
        분석 결과 리스트
    """
    try:
        results = storage_service.get_analysis_results(
            file_id=file_id,
            uid=uid,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
    except Exception as e:
        logger.error(f"분석 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{analysis_id}")
async def get_analysis_by_id(analysis_id: str):
    """특정 분석 결과 조회"""
    try:
        result = storage_service.get_analysis_by_id(analysis_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="분석 결과를 찾을 수 없습니다.")
        
        return {
            "success": True,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"분석 결과 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def get_analysis_jobs(
    status: Optional[str] = Query(None, description="작업 상태로 필터링"),
    limit: int = Query(50, description="결과 수 제한")
):
    """분석 작업 목록 조회"""
    try:
        jobs = storage_service.get_analysis_jobs(status=status, limit=limit)
        
        return {
            "success": True,
            "jobs": jobs,
            "count": len(jobs)
        }
    except Exception as e:
        logger.error(f"분석 작업 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_analysis_statistics(
    days: int = Query(30, description="통계 기간 (일)")
):
    """분석 통계 조회"""
    try:
        stats = storage_service.get_analysis_statistics(days=days)
        
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        logger.error(f"분석 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_analysis_results(
    search_term: str = Query(..., description="검색어"),
    search_type: str = Query("opinion", description="검색 타입 (opinion, uid, filename)"),
    limit: int = Query(50, description="결과 수 제한")
):
    """분석 결과 검색"""
    try:
        results = storage_service.search_analysis_results(
            search_term=search_term,
            search_type=search_type,
            limit=limit
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "search_info": {
                "term": search_term,
                "type": search_type
            }
        }
    except Exception as e:
        logger.error(f"분석 결과 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score-distribution")
async def get_score_distribution(
    score_type: str = Query("hybrid_score", description="점수 타입")
):
    """점수 분포 조회"""
    try:
        distribution = storage_service.get_score_distribution(score_type=score_type)
        
        return {
            "success": True,
            "distribution": distribution
        }
    except Exception as e:
        logger.error(f"점수 분포 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_old_results(
    retention_days: int = Query(365, description="보관 기간 (일)")
):
    """오래된 분석 결과 정리"""
    try:
        storage_service.cleanup_old_results(retention_days=retention_days)
        
        return {
            "success": True,
            "message": f"{retention_days}일 이전 분석 결과를 정리했습니다."
        }
    except Exception as e:
        logger.error(f"분석 결과 정리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export")
async def export_analysis_results(
    file_id: Optional[str] = Query(None, description="파일 ID로 필터링"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD)"),
    format: str = Query("json", description="내보내기 형식 (json, csv)")
):
    """분석 결과 내보내기"""
    try:
        # 기본 조회
        results = storage_service.get_analysis_results(
            file_id=file_id,
            limit=10000  # 대량 내보내기를 위해 높은 제한
        )
        
        # 날짜 필터링 (필요한 경우)
        if start_date or end_date:
            # 날짜 필터링 로직 구현
            pass
        
        if format == "csv":
            # CSV 형식으로 변환
            import pandas as pd
            df = pd.DataFrame(results)
            csv_data = df.to_csv(index=False)
            
            return {
                "success": True,
                "format": "csv",
                "data": csv_data,
                "count": len(results)
            }
        else:
            # JSON 형식
            return {
                "success": True,
                "format": "json",
                "data": results,
                "count": len(results)
            }
            
    except Exception as e:
        logger.error(f"분석 결과 내보내기 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
