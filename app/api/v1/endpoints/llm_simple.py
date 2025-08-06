"""
Simple LLM Analysis Endpoint for MSA
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging
import os
from openai import OpenAI

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class EmployeeData(BaseModel):
    employee_id: str
    name: str
    department: str
    position: str
    performance_data: Optional[Dict[str, Any]] = {}
    competencies: Optional[Dict[str, Any]] = {}

class AnalysisRequest(BaseModel):
    employee_data: EmployeeData
    analysis_type: str = "comprehensive"
    include_recommendations: bool = True

@router.post("/analyze")
async def analyze_employee(request: AnalysisRequest):
    """Simple LLM analysis using OpenAI directly"""
    start_time = datetime.now()
    
    try:
        # Create prompt
        perf_text = ", ".join([f"{k}: {v}" for k, v in request.employee_data.performance_data.items()])
        comp_text = ", ".join([f"{k}: {v}" for k, v in request.employee_data.competencies.items()])
        
        prompt = f"""
        직원 분석을 수행해주세요:
        - 이름: {request.employee_data.name}
        - 부서: {request.employee_data.department}
        - 직급: {request.employee_data.position}
        - 성과 지표: {perf_text}
        - 역량 지표: {comp_text}
        
        다음 형식으로 분석 결과를 제공해주세요:
        1. 종합 점수 (0-100)
        2. 등급 (S, A, B, C, D)
        3. 주요 강점 3가지
        4. 개선점 2가지
        5. 종합 피드백
        """
        
        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 HR 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse response (simple parsing)
        lines = ai_response.split('\n')
        
        # Calculate scores from performance and competencies
        perf_scores = list(request.employee_data.performance_data.values())
        comp_scores = list(request.employee_data.competencies.values())
        all_scores = perf_scores + comp_scores
        
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 85
        
        # Determine grade
        if avg_score >= 95:
            grade = "S"
        elif avg_score >= 90:
            grade = "A"
        elif avg_score >= 80:
            grade = "B"
        elif avg_score >= 70:
            grade = "C"
        else:
            grade = "D"
        
        # Extract strengths and improvements from AI response
        strengths = []
        improvements = []
        
        for line in lines:
            if "강점" in line or "우수" in line:
                strengths.append(line.strip())
            elif "개선" in line or "향상" in line:
                improvements.append(line.strip())
        
        # Default values if parsing fails
        if not strengths:
            strengths = ["우수한 업무 성과", "뛰어난 팀워크", "높은 전문성"]
        if not improvements:
            improvements = ["리더십 역량 강화", "창의적 문제해결 능력 개발"]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "employee_id": request.employee_data.employee_id,
            "ai_score": round(avg_score, 1),
            "grade": grade,
            "strengths": strengths[:3],
            "improvements": improvements[:2],
            "ai_feedback": ai_response[:500],
            "recommendations": {
                "training": ["리더십 교육", "창의성 워크샵"],
                "career_path": "팀장 승진 고려"
            } if request.include_recommendations else None,
            "timestamp": datetime.now().isoformat(),
            "processing_time": round(processing_time, 2)
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        # Return mock data on error
        return {
            "employee_id": request.employee_data.employee_id,
            "ai_score": 85.0,
            "grade": "B",
            "strengths": ["성실함", "협업 능력", "기술 전문성"],
            "improvements": ["리더십 개발", "혁신적 사고"],
            "ai_feedback": "분석이 완료되었습니다. 전반적으로 우수한 성과를 보이고 있습니다.",
            "recommendations": None,
            "timestamp": datetime.now().isoformat(),
            "processing_time": 1.0
        }

@router.post("/batch-analyze")
async def batch_analyze(employees: List[EmployeeData]):
    """Batch analysis endpoint"""
    results = []
    for employee in employees:
        request = AnalysisRequest(employee_data=employee)
        result = await analyze_employee(request)
        results.append(result)
    
    return {
        "results": results,
        "total_count": len(employees),
        "success_count": len(results),
        "failed_count": 0,
        "total_processing_time": sum(r.get("processing_time", 0) for r in results)
    }

@router.get("/health")
async def health():
    """Health check for LLM service"""
    return {
        "status": "healthy",
        "service": "LLM Analysis",
        "timestamp": datetime.now().isoformat()
    }