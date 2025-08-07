"""
AIRISS v4.2 직원별 AI 분석 API
Employee AI Analysis REST API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.db.database import get_db
from app.schemas.employee import (
    EmployeeAIAnalysis,
    EmployeeAIAnalysisList,
    AIRecommendation,
    AIFeedbackSave,
    AIFeedbackResponse,
    DashboardStatistics
)
from app.services.employee_service import EmployeeService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("")
@router.get("/")
async def get_employees_list(db: Session = Depends(get_db)):
    """
    전체 직원 목록 간단 조회
    """
    try:
        service = EmployeeService(db)
        result = service.get_employees_ai_analysis_list(
            filters={},
            sort_options={"field": "ai_score", "order": "desc"},
            pagination={"page": 1, "page_size": 100}  # 최대값 100으로 수정
        )
        return result
    except Exception as e:
        logger.error(f"직원 목록 조회 실패: {e}")
        return {"results": [], "total": 0}

@router.get("/{employee_id}/ai-analysis", response_model=EmployeeAIAnalysis)
async def get_employee_ai_analysis(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """
    특정 직원의 AI 분석 결과 상세 조회
    
    - **employee_id**: 직원 ID
    - **returns**: 직원의 AI 분석 결과 (점수, 등급, 역량, 강점, 개선점, AI 코멘트 등)
    """
    try:
        service = EmployeeService(db)
        result = service.get_employee_ai_analysis(employee_id)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"직원 {employee_id}의 AI 분석 결과를 찾을 수 없습니다.")
        
        return result
    except Exception as e:
        logger.error(f"직원 AI 분석 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-analysis/list", response_model=EmployeeAIAnalysisList)
async def get_employees_ai_analysis_list(
    department: Optional[str] = Query(None, description="부서명 필터"),
    position: Optional[str] = Query(None, description="직급 필터"),
    grade: Optional[str] = Query(None, description="AI 등급 필터 (S, A+, A, B, C, D)"),
    min_score: Optional[int] = Query(None, description="최소 AI 점수"),
    max_score: Optional[int] = Query(None, description="최대 AI 점수"),
    search: Optional[str] = Query(None, description="이름 또는 직원번호 검색"),
    sort_by: Optional[str] = Query("ai_score", description="정렬 기준 (ai_score, name, department)"),
    sort_order: Optional[str] = Query("desc", description="정렬 순서 (asc, desc)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    db: Session = Depends(get_db)
):
    """
    전체 직원 AI 분석 목록 조회 (필터/검색/정렬)
    
    - **필터**: 부서, 직급, AI등급, AI점수 범위
    - **검색**: 이름 또는 직원번호
    - **정렬**: AI점수, 이름, 부서별
    - **페이징**: 페이지 번호와 크기 지정
    """
    try:
        service = EmployeeService(db)
        
        # 필터 조건 구성
        filters = {
            "department": department,
            "position": position,
            "grade": grade,
            "min_score": min_score,
            "max_score": max_score,
            "search": search
        }
        
        # 정렬 옵션
        sort_options = {
            "field": sort_by,
            "order": sort_order
        }
        
        # 페이징 옵션
        pagination = {
            "page": page,
            "page_size": page_size
        }
        
        result = service.get_employees_ai_analysis_list(
            filters=filters,
            sort_options=sort_options,
            pagination=pagination
        )
        
        return result
    except Exception as e:
        logger.error(f"직원 AI 분석 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ai-recommendation", response_model=List[AIRecommendation])
async def get_ai_recommendations(
    type: str = Query(..., description="추천 유형 (talent, promotion, risk, leadership)"),
    limit: int = Query(10, ge=1, le=50, description="결과 개수 제한"),
    db: Session = Depends(get_db)
):
    """
    AI 추천 인재/리더십 후보 리스트
    
    - **type**: 추천 유형
      - talent: Top Talent (고성과자)
      - promotion: 승진 후보자
      - risk: 이직 위험군
      - leadership: 리더십 잠재력
    - **limit**: 반환할 최대 인원 수
    """
    try:
        service = EmployeeService(db)
        
        if type not in ["talent", "promotion", "risk", "leadership"]:
            raise HTTPException(status_code=400, detail="유효하지 않은 추천 유형입니다.")
        
        result = service.get_ai_recommendations(
            recommendation_type=type,
            limit=limit
        )
        
        return result
    except Exception as e:
        logger.error(f"AI 추천 리스트 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-feedback/save", response_model=AIFeedbackResponse)
async def save_ai_feedback(
    feedback: AIFeedbackSave,
    db: Session = Depends(get_db)
):
    """
    AI 분석/피드백 내역 저장
    
    - **employee_id**: 직원 ID
    - **ai_feedback_text**: AI 피드백 텍스트
    - **action**: 저장 액션 타입 (save_to_record, send_email, etc.)
    - **additional_data**: 추가 데이터 (선택사항)
    """
    try:
        service = EmployeeService(db)
        
        result = service.save_ai_feedback(
            employee_id=feedback.employee_id,
            feedback_text=feedback.ai_feedback_text,
            action=feedback.action,
            additional_data=feedback.additional_data
        )
        
        return AIFeedbackResponse(
            success=True,
            message="AI 피드백이 성공적으로 저장되었습니다.",
            feedback_id=result.get("feedback_id"),
            saved_at=result.get("saved_at")
        )
    except Exception as e:
        logger.error(f"AI 피드백 저장 실패: {e}")
        return AIFeedbackResponse(
            success=False,
            message=f"AI 피드백 저장 실패: {str(e)}",
            feedback_id=None,
            saved_at=None
        )

@router.get("/{employee_id}/competency-radar-data")
async def get_competency_radar_data(
    employee_id: str,
    db: Session = Depends(get_db)
):
    """
    직원의 8대 역량 레이더 차트 데이터 조회
    
    - **employee_id**: 직원 ID
    - **returns**: 레이더 차트용 역량 데이터
    """
    try:
        service = EmployeeService(db)
        result = service.get_competency_radar_data(employee_id)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"직원 {employee_id}의 역량 데이터를 찾을 수 없습니다.")
        
        return result
    except Exception as e:
        logger.error(f"역량 레이더 데이터 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/statistics", response_model=DashboardStatistics)
async def get_dashboard_statistics(
    department: Optional[str] = Query(None, description="부서별 통계"),
    db: Session = Depends(get_db)
):
    """
    대시보드용 전체 통계 데이터
    
    - **department**: 특정 부서만 필터링 (선택사항)
    - **returns**: 등급 분포, 평균 점수, 역량 통계 등
    """
    try:
        service = EmployeeService(db)
        result = service.get_dashboard_statistics(department)
        
        return result
    except Exception as e:
        logger.error(f"대시보드 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/employee-results")
async def debug_employee_results(db: Session = Depends(get_db)):
    """디버깅용: EmployeeResult 테이블 상태 확인"""
    try:
        from app.models.employee import EmployeeResult
        from app.models.analysis_result import AnalysisResultModel as AnalysisResult
        from app.models.job import Job
        
        # EmployeeResult 테이블 상태
        employee_total = db.query(EmployeeResult).count()
        employee_recent = db.query(EmployeeResult).limit(10).all()
        
        employee_data = []
        for emp_result in employee_recent:
            employee_data.append({
                "id": emp_result.id,
                "uid": emp_result.uid,
                "job_id": emp_result.job_id,
                "overall_score": emp_result.overall_score,
                "grade": emp_result.grade,
                "employee_metadata": emp_result.employee_metadata
            })
        
        # 기존 AnalysisResult 테이블 상태 (비교용)
        analysis_total = db.query(AnalysisResult).count()
        analysis_recent = db.query(AnalysisResult).limit(5).all()
        
        analysis_data = []
        for analysis in analysis_recent:
            analysis_data.append({
                "id": analysis.id,
                "file_id": analysis.file_id,
                "created_at": str(analysis.created_at),
                "result_preview": str(analysis.result)[:200] if analysis.result else None
            })
        
        # Job 테이블 상태
        job_total = db.query(Job).count()
        job_recent = db.query(Job).limit(5).all()
        
        job_data = []
        for job in job_recent:
            job_data.append({
                "id": job.id,
                "status": job.status,
                "created_at": str(job.created_at),
                "completed_at": str(job.completed_at) if job.completed_at else None
            })
        
        return {
            "employee_results": {
                "total_count": employee_total,
                "recent_data": employee_data
            },
            "analysis_results": {
                "total_count": analysis_total,
                "recent_data": analysis_data
            },
            "jobs": {
                "total_count": job_total,
                "recent_data": job_data
            },
            "message": f"EmployeeResult: {employee_total}개, AnalysisResult: {analysis_total}개, Jobs: {job_total}개"
        }
        
    except Exception as e:
        logger.error(f"디버깅 조회 실패: {e}")
        return {
            "error": str(e),
            "message": "데이터베이스 조회 실패"
        }