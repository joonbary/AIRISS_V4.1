"""
AIRISS LLM Analysis Microservice API
OpenAI를 활용한 HR 분석 전용 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.hybrid_analyzer import AIRISSHybridAnalyzer as HybridAnalyzer
from app.services.text_analyzer import AIRISSTextAnalyzer as TextAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class EmployeeData(BaseModel):
    """직원 데이터 모델"""
    employee_id: str
    name: str
    department: str
    position: str
    performance_data: Optional[Dict[str, Any]] = {}
    competencies: Optional[Dict[str, Any]] = {}
    additional_info: Optional[Dict[str, Any]] = {}

class AnalysisRequest(BaseModel):
    """분석 요청 모델"""
    employee_data: EmployeeData
    analysis_type: str = "comprehensive"  # comprehensive, performance, competency
    include_recommendations: bool = True

class BatchAnalysisRequest(BaseModel):
    """배치 분석 요청 모델"""
    employees: List[EmployeeData]
    analysis_type: str = "comprehensive"
    include_recommendations: bool = True

class AnalysisResponse(BaseModel):
    """분석 응답 모델"""
    employee_id: str
    ai_score: float
    grade: str
    strengths: List[str]
    improvements: List[str]
    ai_feedback: str
    recommendations: Optional[Dict[str, Any]] = None
    timestamp: datetime
    processing_time: float

class BatchAnalysisResponse(BaseModel):
    """배치 분석 응답 모델"""
    results: List[AnalysisResponse]
    total_count: int
    success_count: int
    failed_count: int
    total_processing_time: float

# API Endpoints
@router.post("/analyze")
async def analyze_employee(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    단일 직원 LLM 분석
    
    EHR 시스템에서 직원 데이터를 전송하면 AI 분석 결과 반환
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"🔍 LLM 분석 시작 - 직원 ID: {request.employee_data.employee_id}")
        
        # HybridAnalyzer 초기화
        analyzer = HybridAnalyzer()
        
        # 분석용 데이터 준비
        analysis_data = {
            "UID": request.employee_data.employee_id,
            "이름": request.employee_data.name,
            "부서": request.employee_data.department,
            "직급": request.employee_data.position,
            **request.employee_data.performance_data,
            **request.employee_data.competencies
        }
        
        # LLM 분석 수행 (TextAnalyzer 사용)
        text_analyzer = TextAnalyzer()
        
        # 텍스트 의견 생성
        performance_text = ", ".join([f"{k}: {v}점" for k, v in request.employee_data.performance_data.items()])
        competency_text = ", ".join([f"{k}: {v}점" for k, v in request.employee_data.competencies.items()])
        opinion = f"{request.employee_data.name}님은 {request.employee_data.department} {request.employee_data.position}입니다. 성과: {performance_text}. 역량: {competency_text}"
        
        # 비동기 분석 수행
        import asyncio
        result = asyncio.run(text_analyzer.analyze_text(
            uid=request.employee_data.employee_id,
            opinion=opinion
        ))
        
        # 처리 시간 계산
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 응답 생성
        response = {
            "employee_id": request.employee_data.employee_id,
            "ai_score": result.get("overall_score", result.get("score", 85)),
            "grade": result.get("grade", "B"),
            "strengths": result.get("strengths", ["성실함", "팀워크", "기술력"]),
            "improvements": result.get("improvements", ["리더십 개발", "창의성 향상"]),
            "ai_feedback": result.get("ai_feedback", result.get("feedback", "종합적으로 우수한 직원입니다.")),
            "recommendations": result.get("recommendations") if request.include_recommendations else None,
            "timestamp": datetime.now().isoformat(),
            "processing_time": processing_time
        }
        
        logger.info(f"✅ LLM 분석 완료 - 직원 ID: {request.employee_data.employee_id}, 처리 시간: {processing_time}초")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ LLM 분석 실패 - 직원 ID: {request.employee_data.employee_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")

@router.post("/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze_employees(
    request: BatchAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    대량 직원 LLM 분석
    
    여러 직원의 데이터를 한 번에 분석
    """
    start_time = datetime.now()
    results = []
    success_count = 0
    failed_count = 0
    
    try:
        logger.info(f"📊 배치 분석 시작 - 총 {len(request.employees)}명")
        
        # HybridAnalyzer 초기화 (재사용)
        analyzer = HybridAnalyzer()
        
        for employee in request.employees:
            try:
                # 각 직원 분석
                analysis_data = {
                    "UID": employee.employee_id,
                    "이름": employee.name,
                    "부서": employee.department,
                    "직급": employee.position,
                    **employee.performance_data,
                    **employee.competencies
                }
                
                # TextAnalyzer 사용
                text_analyzer = TextAnalyzer()
                performance_text = ", ".join([f"{k}: {v}점" for k, v in employee.performance_data.items()])
                competency_text = ", ".join([f"{k}: {v}점" for k, v in employee.competencies.items()])
                opinion = f"{employee.name}님은 {employee.department} {employee.position}입니다. 성과: {performance_text}. 역량: {competency_text}"
                
                import asyncio
                result = asyncio.run(text_analyzer.analyze_text(
                    uid=employee.employee_id,
                    opinion=opinion
                ))
                
                # 개별 처리 시간
                individual_processing_time = (datetime.now() - start_time).total_seconds() / (success_count + 1)
                
                results.append(AnalysisResponse(
                    employee_id=employee.employee_id,
                    ai_score=result.get("overall_score", 0),
                    grade=result.get("grade", "B"),
                    strengths=result.get("strengths", []),
                    improvements=result.get("improvements", []),
                    ai_feedback=result.get("ai_feedback", ""),
                    recommendations=result.get("recommendations") if request.include_recommendations else None,
                    timestamp=datetime.now(),
                    processing_time=individual_processing_time
                ))
                success_count += 1
                
            except Exception as e:
                logger.error(f"❌ 직원 {employee.employee_id} 분석 실패: {str(e)}")
                failed_count += 1
                
                # 실패한 경우에도 결과에 포함 (에러 표시)
                results.append(AnalysisResponse(
                    employee_id=employee.employee_id,
                    ai_score=0,
                    grade="N/A",
                    strengths=[],
                    improvements=[],
                    ai_feedback=f"분석 실패: {str(e)}",
                    recommendations=None,
                    timestamp=datetime.now(),
                    processing_time=0
                ))
        
        # 전체 처리 시간
        total_processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ 배치 분석 완료 - 성공: {success_count}, 실패: {failed_count}, 총 시간: {total_processing_time}초")
        
        return BatchAnalysisResponse(
            results=results,
            total_count=len(request.employees),
            success_count=success_count,
            failed_count=failed_count,
            total_processing_time=total_processing_time
        )
        
    except Exception as e:
        logger.error(f"❌ 배치 분석 전체 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"배치 분석 중 오류 발생: {str(e)}")

@router.get("/health")
async def health_check():
    """
    서비스 상태 확인
    
    LLM 서비스 및 OpenAI API 연결 상태 확인
    """
    try:
        # OpenAI API 키 확인
        import os
        api_key_exists = bool(os.getenv("OPENAI_API_KEY"))
        
        # 간단한 테스트 분석
        if api_key_exists:
            analyzer = TextAnalyzer()
            test_result = analyzer.test_connection()
            openai_status = "connected" if test_result else "error"
        else:
            openai_status = "no_api_key"
        
        return {
            "status": "healthy" if openai_status == "connected" else "degraded",
            "service": "AIRISS LLM Analysis Service",
            "version": "1.0.0",
            "openai_status": openai_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/usage")
async def get_usage_statistics(db: Session = Depends(get_db)):
    """
    API 사용 통계
    
    OpenAI API 사용량 및 분석 통계 반환
    """
    try:
        # 실제로는 DB에서 통계 조회
        # 여기서는 예시 데이터 반환
        return {
            "total_analyses": 1234,
            "today_analyses": 45,
            "average_processing_time": 2.5,
            "openai_tokens_used": 150000,
            "estimated_cost": 3.75,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")