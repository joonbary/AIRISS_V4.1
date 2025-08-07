# app/api/v1/api.py
"""
AIRISS v4.0 API 라우터
모든 v1 엔드포인트 통합
"""

from fastapi import APIRouter
from app.api.v1.endpoints import analysis, employee, analysis_opinion, analysis_opinion_simple, config, hr_dashboard

api_router = APIRouter()

# 분석 관련 엔드포인트
api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["analysis"]
)

# 평가의견 분석 엔드포인트
api_router.include_router(
    analysis_opinion.router,
    prefix="/analysis/opinion",
    tags=["opinion_analysis"]
)

# 평가의견 분석 테스트 엔드포인트
api_router.include_router(
    analysis_opinion_simple.router,
    prefix="/analysis/opinion/simple",
    tags=["opinion_test"]
)

# 직원 관련 엔드포인트
api_router.include_router(
    employee.router,
    prefix="/employee",
    tags=["employee"]
)

# 설정 관련 엔드포인트
api_router.include_router(
    config.router,
    prefix="/config",
    tags=["config"]
)

# HR 대시보드 엔드포인트
api_router.include_router(
    hr_dashboard.router,
    prefix="/hr-dashboard",
    tags=["hr_dashboard"]
)

# 향후 추가 엔드포인트
# api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
# api_router.include_router(reports.router, prefix="/reports", tags=["reports"])