# app/middleware/monitoring.py
# AIRISS v4.0 통합 모니터링 미들웨어 - 성능/에러/사용자 분석

import time
import json
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import asyncio
import psutil
# (sqlite3 관련 코드 전체 삭제)
from pathlib import Path

# 로깅 설정
logger = logging.getLogger(__name__)

class AIRISSMonitoringMiddleware(BaseHTTPMiddleware):
    """AIRISS v4.0 통합 모니터링 미들웨어"""
    
    def __init__(self, app, db_path: str = "monitoring.db"):
        super().__init__(app)
        self.db_path = db_path
        # (sqlite3 관련 코드 전체 삭제)
        
        # 성능 메트릭 저장용
        self.metrics = {
            "requests_total": 0,
            "requests_failed": 0,
            "response_times": [],
            "active_connections": 0,
            "memory_usage": [],
            "cpu_usage": []
        }
        
        # 백그라운드 모니터링 태스크 시작
        asyncio.create_task(self.background_monitoring())
    
    # (sqlite3 관련 코드 전체 삭제)
    
    async def dispatch(self, request: Request, call_next):
        """요청 처리 및 모니터링"""
        start_time = time.time()
        
        # 요청 정보 수집
        user_agent = request.headers.get("user-agent", "")
        ip_address = self.get_client_ip(request)
        user_id = self.extract_user_id(request)
        
        # 활성 연결 수 증가
        self.metrics["active_connections"] += 1
        
        try:
            # 요청 처리
            response = await call_next(request)
            
            # 응답 시간 계산
            response_time = time.time() - start_time
            self.metrics["response_times"].append(response_time)
            
            # 요청 로그 저장
            # (sqlite3 관련 코드 전체 삭제)
            
            # 성능 메트릭 업데이트
            self.metrics["requests_total"] += 1
            if response.status_code >= 400:
                self.metrics["requests_failed"] += 1
            
            # 사용자 활동 로그
            if user_id:
                # (sqlite3 관련 코드 전체 삭제)
                pass # Placeholder for user activity logging
            
            return response
            
        except Exception as e:
            # 에러 처리 및 로깅
            response_time = time.time() - start_time
            
            # (sqlite3 관련 코드 전체 삭제)
            pass # Placeholder for error logging
            
            self.metrics["requests_failed"] += 1
            
            # 에러 응답 생성
            return Response(
                content=json.dumps({
                    "error": "Internal Server Error",
                    "message": "시스템 오류가 발생했습니다.",
                    "timestamp": datetime.now().isoformat()
                }),
                status_code=500,
                media_type="application/json"
            )
        
        finally:
            # 활성 연결 수 감소
            self.metrics["active_connections"] -= 1
    
    def get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 주소 추출"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return str(request.client.host) if request.client else "unknown"
    
    def extract_user_id(self, request: Request) -> Optional[str]:
        """요청에서 사용자 ID 추출 (향후 인증 시스템과 연동)"""
        # 현재는 세션 기반으로 임시 ID 생성
        session_id = request.headers.get("x-session-id")
        if session_id:
            return f"session_{session_id}"
        
        # IP 기반 임시 ID
        return f"ip_{self.get_client_ip(request)}"
    
    # (sqlite3 관련 코드 전체 삭제)
    
    # (sqlite3 관련 코드 전체 삭제)
    
    # (sqlite3 관련 코드 전체 삭제)
    
    async def background_monitoring(self):
        """백그라운드 시스템 모니터링"""
        while True:
            try:
                # 시스템 메트릭 수집
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # 요청 속도 계산 (분당 요청 수)
                current_time = time.time()
                recent_requests = len([
                    rt for rt in self.metrics["response_times"][-60:]  # 최근 60초
                ])
                
                # 메트릭 저장
                # (sqlite3 관련 코드 전체 삭제)
                
                # 메모리 정리 (오래된 데이터 제거)
                if len(self.metrics["response_times"]) > 1000:
                    self.metrics["response_times"] = self.metrics["response_times"][-500:]
                
                # 60초마다 실행
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"백그라운드 모니터링 오류: {e}")
                await asyncio.sleep(60)
    
    # (sqlite3 관련 코드 전체 삭제)
    
    # (sqlite3 관련 코드 전체 삭제)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """현재 메트릭 요약 반환"""
        avg_response_time = (
            sum(self.metrics["response_times"][-100:]) / 
            len(self.metrics["response_times"][-100:])
            if self.metrics["response_times"] else 0
        )
        
        error_rate = (
            (self.metrics["requests_failed"] / self.metrics["requests_total"]) * 100
            if self.metrics["requests_total"] > 0 else 0
        )
        
        return {
            "total_requests": self.metrics["requests_total"],
            "failed_requests": self.metrics["requests_failed"],
            "error_rate_percent": round(error_rate, 2),
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "active_connections": self.metrics["active_connections"],
            "uptime_seconds": time.time() - self.start_time if hasattr(self, 'start_time') else 0
        }


class MonitoringAPI:
    """모니터링 데이터 조회 API"""
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
    
    def get_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """모니터링 대시보드 데이터 조회"""
        try:
            # (sqlite3 관련 코드 전체 삭제)
            pass # Placeholder for database connection and query
            
            # 시간 범위 설정
            since = datetime.now() - timedelta(hours=hours)
            
            # 요청 통계
            # (sqlite3 관련 코드 전체 삭제)
            request_stats = (0, 0, 0.0, 0.0) # Placeholder
            
            # 시간별 요청 수
            # (sqlite3 관련 코드 전체 삭제)
            hourly_requests = [] # Placeholder
            
            # 최근 에러 로그
            # (sqlite3 관련 코드 전체 삭제)
            recent_errors = [] # Placeholder
            
            # 시스템 메트릭 (최근 값)
            # (sqlite3 관련 코드 전체 삭제)
            system_metrics = (0.0, 0.0, 0.0, 0.0, 0, 0.0) # Placeholder
            
            # 인기 페이지
            # (sqlite3 관련 코드 전체 삭제)
            popular_pages = [] # Placeholder
            
            # (sqlite3 관련 코드 전체 삭제)
            
            return {
                "request_stats": {
                    "total": request_stats[0] or 0,
                    "failed": request_stats[1] or 0,
                    "error_rate": round((request_stats[1] / request_stats[0] * 100) if request_stats[0] > 0 else 0, 2),
                    "avg_response_time": round((request_stats[2] or 0) * 1000, 2),  # ms로 변환
                    "max_response_time": round((request_stats[3] or 0) * 1000, 2)
                },
                "hourly_requests": hourly_requests,
                "recent_errors": recent_errors,
                "system_metrics": {
                    "cpu_percent": system_metrics[0] if system_metrics else 0,
                    "memory_percent": system_metrics[1] if system_metrics else 0,
                    "memory_used_mb": system_metrics[2] if system_metrics else 0,
                    "disk_percent": system_metrics[3] if system_metrics else 0,
                    "active_connections": system_metrics[4] if system_metrics else 0,
                    "requests_per_minute": system_metrics[5] if system_metrics else 0
                },
                "popular_pages": popular_pages,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"대시보드 데이터 조회 실패: {e}")
            return {"error": str(e)}
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """성능 트렌드 데이터 조회"""
        try:
            # (sqlite3 관련 코드 전체 삭제)
            pass # Placeholder for database connection and query
            
            since = datetime.now() - timedelta(days=days)
            
            # 일별 성능 지표
            # (sqlite3 관련 코드 전체 삭제)
            daily_performance = [] # Placeholder
            
            # 시스템 리소스 트렌드
            # (sqlite3 관련 코드 전체 삭제)
            resource_trends = [] # Placeholder
            
            # (sqlite3 관련 코드 전체 삭제)
            
            return {
                "daily_performance": daily_performance,
                "resource_trends": resource_trends,
                "period_days": days,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"성능 트렌드 조회 실패: {e}")
            return {"error": str(e)}


# FastAPI 라우터에 추가할 모니터링 엔드포인트들
from fastapi import APIRouter

monitoring_router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

@monitoring_router.get("/dashboard")
async def get_monitoring_dashboard(hours: int = 24):
    """모니터링 대시보드 데이터 조회"""
    api = MonitoringAPI()
    return api.get_dashboard_data(hours)

@monitoring_router.get("/performance")
async def get_performance_trends(days: int = 7):
    """성능 트렌드 데이터 조회"""
    api = MonitoringAPI()
    return api.get_performance_trends(days)

@monitoring_router.get("/health/detailed")
async def get_detailed_health():
    """상세 헬스 체크"""
    try:
        # 시스템 정보
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 데이터베이스 연결 테스트
        db_healthy = True
        try:
            # (sqlite3 관련 코드 전체 삭제)
            pass # Placeholder for database connection test
        except:
            db_healthy = False
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "services": {
                "database": "healthy" if db_healthy else "unhealthy",
                "monitoring": "healthy"
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }