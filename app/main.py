# -*- coding: utf-8 -*-
"""
AIRISS v5.0 Main Application
OK Financial Group HR Analysis System
"""
# Standard library imports
import logging
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Third-party imports
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv(override=True)

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Local imports
from app.db.database import get_db, engine, init_db
from app.models import Base

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 시간대 설정
KST = timezone(timedelta(hours=9))

# 개인별 맞춤 사유 생성 함수들
def generate_risk_reason(score, dimension_scores, position, department):
    """개별 직원의 위험 요인에 대한 구체적 사유 생성"""
    import random
    
    # 역량별 한글 매핑
    competency_mapping = {
        "실행력": "실행력", "execution": "실행력",
        "성장지향": "성장지향", "growth": "성장지향",
        "협업": "협업", "collaboration": "협업", "teamwork": "협업",
        "고객지향": "고객지향", "customer_focus": "고객지향",
        "전문성": "전문성", "expertise": "전문성", "technical": "전문성",
        "혁신성": "혁신성", "innovation": "혁신성",
        "리더십": "리더십", "leadership": "리더십",
        "커뮤니케이션": "커뮤니케이션", "communication": "커뮤니케이션"
    }
    
    # 역량 데이터 정규화
    normalized_scores = {}
    for key, value in dimension_scores.items():
        mapped_key = competency_mapping.get(key, key)
        if mapped_key and isinstance(value, (int, float)):
            normalized_scores[mapped_key] = value
    
    # 가장 낮은 역량 찾기
    if normalized_scores:
        lowest_competency = min(normalized_scores, key=normalized_scores.get)
        lowest_score = normalized_scores[lowest_competency]
    else:
        lowest_competency = "기본 역량"
        lowest_score = score
    
    # 점수 구간별 기본 사유
    if score < 40:
        base_reasons = [
            f"{lowest_competency} 역량 심각한 저하 - 즉시 집중 관리 필요",
            f"업무 성과 지속 부진 - {lowest_competency} 개선 시급",
            f"조직 적응도 낮음 - {lowest_competency} 훈련 및 멘토링 필요"
        ]
    else:  # 40-60점
        base_reasons = [
            f"{lowest_competency} 역량 개발 필요 - 체계적 훈련 프로그램 참여",
            f"업무 이해도 부족 - {lowest_competency} 중심 역량 강화 필요",
            f"팀 내 기여도 개선 필요 - {lowest_competency} 스킬 향상 권장"
        ]
    
    # 부서별 특화 사유 추가
    department_specific = {
        "영업": f"고객 응대 및 {lowest_competency} 역량 보완 필요",
        "마케팅": f"창의적 사고와 {lowest_competency} 능력 향상 필요", 
        "개발": f"기술 역량 및 {lowest_competency} 스킬 개발 필요",
        "HR": f"소통 능력 및 {lowest_competency} 역량 강화 필요",
        "재무": f"분석 역량 및 {lowest_competency} 능력 개선 필요"
    }
    
    # 부서 매칭 시도
    dept_reason = None
    if department:
        for dept_key in department_specific:
            if dept_key in department:
                dept_reason = department_specific[dept_key]
                break
    
    # 최종 사유 선택
    if dept_reason:
        return dept_reason
    else:
        return random.choice(base_reasons)

def generate_promotion_reason(score, dimension_scores, position, department, grade):
    """개별 직원의 승진 사유 생성"""
    import random
    
    # 역량별 한글 매핑
    competency_mapping = {
        "실행력": "실행력", "execution": "실행력",
        "성장지향": "성장지향", "growth": "성장지향", 
        "협업": "협업", "collaboration": "협업", "teamwork": "협업",
        "고객지향": "고객지향", "customer_focus": "고객지향",
        "전문성": "전문성", "expertise": "전문성", "technical": "전문성",
        "혁신성": "혁신성", "innovation": "혁신성",
        "리더십": "리더십", "leadership": "리더십",
        "커뮤니케이션": "커뮤니케이션", "communication": "커뮤니케이션"
    }
    
    # 역량 데이터 정규화 및 상위 역량 찾기
    normalized_scores = {}
    for key, value in dimension_scores.items():
        mapped_key = competency_mapping.get(key, key)
        if mapped_key and isinstance(value, (int, float)):
            normalized_scores[mapped_key] = value
    
    if normalized_scores:
        # 상위 2개 역량 선택
        top_competencies = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)[:2]
        primary_strength = top_competencies[0][0] if top_competencies else "종합 역량"
        secondary_strength = top_competencies[1][0] if len(top_competencies) > 1 else "업무 역량"
    else:
        primary_strength = "종합 역량"
        secondary_strength = "업무 역량"
    
    # 등급별 승진 사유
    grade_reasons = {
        "S": [
            f"탁월한 {primary_strength}와 {secondary_strength}으로 조직 견인",
            f"지속적 최고 성과 달성 - {primary_strength} 분야 전문가",
            f"조직 혁신 주도 - {primary_strength} 기반 탁월한 리더십"
        ],
        "A+": [
            f"우수한 {primary_strength} 역량으로 팀 성과 향상 기여",
            f"{primary_strength}와 {secondary_strength} 균형잡힌 고성과자",
            f"지속적 성장세 - {primary_strength} 중심 핵심 역할 수행"
        ],
        "A": [
            f"안정적 고성과 - {primary_strength} 역량 기반 신뢰성 확보",
            f"{primary_strength} 분야 전문성으로 팀 내 핵심 역할",
            f"꾸준한 성과 개선 - {primary_strength} 중심 발전 가능성"
        ]
    }
    
    # 부서별 특화 승진 사유
    department_reasons = {
        "영업": f"탁월한 {primary_strength}으로 매출 목표 초과 달성",
        "마케팅": f"창의적 {primary_strength}과 전략적 사고로 브랜드 가치 향상",
        "개발": f"뛰어난 {primary_strength}과 기술 혁신으로 프로젝트 성공 견인",
        "HR": f"우수한 {primary_strength}과 소통 능력으로 조직 화합 증진",
        "재무": f"정확한 {primary_strength}과 분석 능력으로 경영 의사결정 지원"
    }
    
    # 부서별 사유 우선, 없으면 등급별 사유
    if department:
        for dept_key in department_reasons:
            if dept_key in department:
                return department_reasons[dept_key]
    
    # 등급별 기본 사유
    grade_specific_reasons = grade_reasons.get(grade, grade_reasons.get("A", []))
    return random.choice(grade_specific_reasons) if grade_specific_reasons else f"우수한 {primary_strength} 역량으로 승진 추천"

def generate_talent_reason(score, dimension_scores, position, department, grade):
    """개별 직원의 핵심인재 사유 생성"""
    import random
    
    # 역량별 한글 매핑
    competency_mapping = {
        "실행력": "실행력", "execution": "실행력",
        "성장지향": "성장지향", "growth": "성장지향",
        "협업": "협업", "collaboration": "협업", "teamwork": "협업", 
        "고객지향": "고객지향", "customer_focus": "고객지향",
        "전문성": "전문성", "expertise": "전문성", "technical": "전문성",
        "혁신성": "혁신성", "innovation": "혁신성",
        "리더십": "리더십", "leadership": "리더십",
        "커뮤니케이션": "커뮤니케이션", "communication": "커뮤니케이션"
    }
    
    # 역량 데이터 정규화 및 최고 역량 찾기
    normalized_scores = {}
    for key, value in dimension_scores.items():
        mapped_key = competency_mapping.get(key, key)
        if mapped_key and isinstance(value, (int, float)):
            normalized_scores[mapped_key] = value
    
    if normalized_scores:
        # 상위 3개 역량 선택
        top_competencies = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        primary_talent = top_competencies[0][0] if top_competencies else "종합 역량"
        secondary_talent = top_competencies[1][0] if len(top_competencies) > 1 else "리더십"
        tertiary_talent = top_competencies[2][0] if len(top_competencies) > 2 else "협업"
        
        # 평균 상위 역량 점수
        avg_top_score = sum([comp[1] for comp in top_competencies[:2]]) / min(2, len(top_competencies))
    else:
        primary_talent = "종합 역량"
        secondary_talent = "리더십"
        tertiary_talent = "협업"
        avg_top_score = score
    
    # 점수 구간별 핵심인재 사유 (85점 이상만 해당)
    if score >= 95:
        base_reasons = [
            f"최고 수준의 {primary_talent}와 {secondary_talent}으로 조직 성장 견인",
            f"탁월한 {primary_talent} 전문성과 혁신적 사고로 업계 리더",
            f"완벽한 {primary_talent}-{secondary_talent}-{tertiary_talent} 균형으로 차세대 리더"
        ]
    elif score >= 90:
        base_reasons = [
            f"뛰어난 {primary_talent}과 {secondary_talent}으로 핵심 프로젝트 성공",
            f"우수한 {primary_talent} 역량과 전략적 사고로 팀 성과 견인",
            f"지속적 혁신과 {primary_talent} 전문성으로 조직 가치 창출"
        ]
    else:  # 85-90점
        base_reasons = [
            f"안정적인 {primary_talent}과 {secondary_talent}으로 중요 업무 담당",
            f"우수한 {primary_talent} 기반 전문성과 성장 잠재력 보유",
            f"균형잡힌 {primary_talent}-{secondary_talent} 역량으로 신뢰성 확보"
        ]
    
    # 부서별 특화 핵심인재 사유
    department_reasons = {
        "영업": f"탁월한 {primary_talent}과 고객 관계 관리로 매출 성장 주도",
        "마케팅": f"창의적 {primary_talent}과 데이터 분석 능력으로 마케팅 혁신",
        "개발": f"뛰어난 {primary_talent}과 기술적 통찰력으로 프로덕트 품질 향상",
        "HR": f"우수한 {primary_talent}과 조직 이해도로 인재 관리 전문가",
        "재무": f"정밀한 {primary_talent}과 전략적 분석으로 재무 의사결정 지원"
    }
    
    # 부서별 사유 우선 적용
    if department:
        for dept_key in department_reasons:
            if dept_key in department:
                return department_reasons[dept_key]
    
    # 기본 사유에서 랜덤 선택
    return random.choice(base_reasons)

# Log environment variables for debugging
env_api_key = os.getenv('OPENAI_API_KEY')
if env_api_key:
    logger.info(f"✅ OPENAI_API_KEY found in environment: {env_api_key[:20]}...")
else:
    logger.warning("⚠️ OPENAI_API_KEY not found in environment variables")

# Try to install OpenAI if not available
try:
    import openai
    logger.info(f"✅ OpenAI already installed: {openai.__version__}")
except ImportError:
    logger.warning("⚠️ OpenAI not found, attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai==1.54.5"])
        import openai
        logger.info(f"✅ OpenAI installed successfully: {openai.__version__}")
    except Exception as e:
        logger.error(f"❌ Failed to install OpenAI: {e}")

# Create FastAPI app
app = FastAPI(
    title="AIRISS v5.0 API",
    description="AI-Powered HR Intelligence & Risk Scoring System",
    version="5.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:8000",
    "https://localhost:3000",
    "https://ehrv10-production.up.railway.app",
    "*"  # Allow all origins for now
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# CSP headers for Railway
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    
    # CSP header for Railway (ehrv10-production.up.railway.app 도메인 허용)
    csp_header = "frame-ancestors 'self' https://ehrv10-production.up.railway.app http://localhost:* https://localhost:*;"
    response.headers["Content-Security-Policy"] = csp_header
    
    # Log the CSP header for debugging
    logger.info(f"Set CSP: {csp_header}")
    
    return response

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create tables"""
    try:
        # Create all tables
        init_db()
        logger.info("Database tables initialized successfully")
        
        # List all tables for verification
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Available tables: {tables}")
        
        # Check if employee_results table exists
        if 'employee_results' in tables:
            logger.info("✅ Employee results table verified")
        else:
            logger.warning("⚠️ Employee results table not found")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Continue anyway - don't crash the app

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    import subprocess
    
    # Git 커밋 정보 가져오기
    try:
        git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()[:8]
    except:
        git_hash = "unknown"
    
    # 템플릿 파일 확인
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    hr_files = []
    if os.path.exists(templates_dir):
        for f in os.listdir(templates_dir):
            if "hr_dashboard" in f:
                hr_files.append(f)
    
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "git_commit": git_hash,
        "hr_dashboard_files": hr_files,
        "deployment_version": "2025-08-07-v5.0.0"
    }

# API endpoint for root - return JSON for API calls
@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {"message": "AIRISS v5.0 API", "version": "5.0.0"}

# HR Dashboard Stats API
@app.get("/api/v1/hr-dashboard/stats")
async def get_hr_dashboard_stats(db: Session = Depends(get_db)):
    """Get HR Dashboard statistics from database"""
    try:
        from sqlalchemy import text
        
        # employee_results 테이블에서 최신 데이터만 조회 (중복 제거)
        result = db.execute(text("""
            WITH latest_records AS (
                SELECT uid, MAX(id::text) as max_id
                FROM employee_results
                WHERE uid IS NOT NULL
                GROUP BY uid
            )
            SELECT COUNT(DISTINCT er.uid) as total_employees,
                   COUNT(CASE WHEN er.overall_score >= 80 THEN 1 END) as high_performers,
                   COUNT(CASE WHEN er.overall_score < 60 THEN 1 END) as risk_employees
            FROM employee_results er
            INNER JOIN latest_records lr ON er.uid = lr.uid AND er.id::text = lr.max_id
        """)).first()
        
        total = result.total_employees if result else 0
        high_performers = result.high_performers if result else 0
        risk_count = result.risk_employees if result else 0
        
        # 위험 직원 목록 조회 (최신 데이터만, 역량 데이터 포함)
        risk_employees = []
        if risk_count > 0:
            risk_results = db.execute(text("""
                WITH latest_records AS (
                    SELECT uid, MAX(id::text) as max_id
                    FROM employee_results
                    WHERE uid IS NOT NULL
                    GROUP BY uid
                )
                SELECT er.uid, 
                       er.employee_metadata->>'name' as name, 
                       er.employee_metadata->>'department' as department, 
                       er.employee_metadata->>'position' as position,
                       er.overall_score,
                       er.dimension_scores,
                       er.grade,
                       CASE 
                           WHEN er.overall_score < 40 THEN 'high'
                           WHEN er.overall_score < 60 THEN 'medium'
                           ELSE 'low'
                       END as risk_level
                FROM employee_results er
                INNER JOIN latest_records lr ON er.uid = lr.uid AND er.id::text = lr.max_id
                WHERE er.overall_score < 60
                ORDER BY er.overall_score ASC
                LIMIT 10
            """)).fetchall()
            
            # 개인별 맞춤 사유 생성
            risk_employees = []
            for r in risk_results:
                # 역량 데이터 파싱
                dimension_scores = r.dimension_scores or {}
                if isinstance(dimension_scores, str):
                    import json
                    try:
                        dimension_scores = json.loads(dimension_scores)
                    except:
                        dimension_scores = {}
                
                # 개인별 사유 생성
                reason = generate_risk_reason(r.overall_score, dimension_scores, r.position, r.department)
                
                risk_employees.append({
                    "uid": r.uid,
                    "name": r.name or "익명",
                    "department": r.department or "-",
                    "ai_score": r.overall_score,
                    "risk_score": r.overall_score,
                    "overall_score": r.overall_score,
                    "risk_level": r.risk_level,
                    "reason": reason
                })
        
        # 승진 후보자 목록 조회 (최신 데이터만, 역량 데이터 포함)
        promotion_candidates = []
        if high_performers > 0:
            promotion_results = db.execute(text("""
                WITH latest_records AS (
                    SELECT uid, MAX(id::text) as max_id
                    FROM employee_results
                    WHERE uid IS NOT NULL
                    GROUP BY uid
                )
                SELECT er.uid, 
                       er.employee_metadata->>'name' as name, 
                       er.employee_metadata->>'department' as department,
                       er.employee_metadata->>'position' as position,
                       er.overall_score,
                       er.dimension_scores,
                       er.grade
                FROM employee_results er
                INNER JOIN latest_records lr ON er.uid = lr.uid AND er.id::text = lr.max_id
                WHERE er.overall_score >= 80 AND er.grade IN ('S', 'A+', 'A', 'B+')
                ORDER BY er.overall_score DESC
                LIMIT 10
            """)).fetchall()
            
            # 개인별 맞춤 사유 생성
            promotion_candidates = []
            for r in promotion_results:
                # 역량 데이터 파싱
                dimension_scores = r.dimension_scores or {}
                if isinstance(dimension_scores, str):
                    import json
                    try:
                        dimension_scores = json.loads(dimension_scores)
                    except:
                        dimension_scores = {}
                
                # 개인별 승진 사유 생성
                reason = generate_promotion_reason(r.overall_score, dimension_scores, r.position, r.department, r.grade)
                
                promotion_candidates.append({
                    "uid": r.uid,
                    "name": r.name or "익명",
                    "department": r.department or "-",
                    "position": r.position or "-",
                    "ai_score": r.overall_score,
                    "overall_score": r.overall_score,
                    "grade": r.grade,
                    "reason": reason
                })
        
        # 핵심 인재 목록 조회 (최신 데이터만, 역량 데이터 포함)
        top_talents = []
        if high_performers > 0:
            talent_results = db.execute(text("""
                WITH latest_records AS (
                    SELECT uid, MAX(id::text) as max_id
                    FROM employee_results
                    WHERE uid IS NOT NULL
                    GROUP BY uid
                )
                SELECT er.uid, 
                       er.employee_metadata->>'name' as name, 
                       er.employee_metadata->>'department' as department,
                       er.employee_metadata->>'position' as position,
                       er.overall_score,
                       er.dimension_scores,
                       er.grade
                FROM employee_results er
                INNER JOIN latest_records lr ON er.uid = lr.uid AND er.id::text = lr.max_id
                WHERE er.overall_score >= 85
                ORDER BY er.overall_score DESC
                LIMIT 10
            """)).fetchall()
            
            # 개인별 맞춤 사유 생성
            top_talents = []
            for r in talent_results:
                # 역량 데이터 파싱
                dimension_scores = r.dimension_scores or {}
                if isinstance(dimension_scores, str):
                    import json
                    try:
                        dimension_scores = json.loads(dimension_scores)
                    except:
                        dimension_scores = {}
                
                # 개인별 핵심인재 사유 생성
                reason = generate_talent_reason(r.overall_score, dimension_scores, r.position, r.department, r.grade)
                
                top_talents.append({
                    "uid": r.uid,
                    "name": r.name or "익명",
                    "department": r.department or "-",
                    "position": r.position or "-",
                    "ai_score": r.overall_score,
                    "overall_score": r.overall_score,
                    "score": r.overall_score,  # 기존 score도 유지
                    "grade": r.grade,
                    "reason": reason
                })
        
        # 전체 직원 목록도 조회 (최신 데이터만)
        all_employees = []
        try:
            employees_query = text("""
                WITH latest_records AS (
                    SELECT uid, MAX(id::text) as max_id
                    FROM employee_results
                    WHERE uid IS NOT NULL
                    GROUP BY uid
                )
                SELECT 
                    er.uid as employee_id,
                    er.employee_metadata->>'name' as employee_name,
                    er.employee_metadata->>'department' as department,
                    er.employee_metadata->>'position' as position,
                    er.overall_score as ai_score,
                    er.grade
                FROM employee_results er
                INNER JOIN latest_records lr ON er.uid = lr.uid AND er.id::text = lr.max_id
                ORDER BY er.overall_score DESC
                LIMIT 1000
            """)
            
            emp_results = db.execute(employees_query).fetchall()
            all_employees = [
                {
                    "employee_id": r.employee_id,
                    "uid": r.employee_id,
                    "name": r.employee_name or "익명",
                    "employee_name": r.employee_name or "익명",
                    "department": r.department or "-",
                    "position": r.position or "-",
                    "ai_score": r.ai_score,
                    "overall_score": r.ai_score,
                    "grade": r.grade
                }
                for r in emp_results
            ]
        except Exception as e:
            logger.warning(f"Failed to get all employees: {e}")
            all_employees = []
        
        return {
            "total_employees": total,
            "promotion_candidates": {
                "count": len(promotion_candidates),
                "employees": promotion_candidates
            },
            "top_talents": {
                "count": len(top_talents),
                "employees": top_talents
            },
            "risk_employees": {
                "count": risk_count,
                "employees": risk_employees
            },
            "employees": all_employees  # 전체 직원 목록 추가
        }
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        return {
            "total_employees": 0,
            "promotion_candidates": {"count": 0, "employees": []},
            "top_talents": {"count": 0, "employees": []},
            "risk_employees": {"count": 0, "employees": []}
        }

# Get Employees List API - 모든 분석 결과 테이블 통합 조회
# DB 연결 테스트 엔드포인트
@app.get("/api/v1/db/test")
async def test_db_connection(db: Session = Depends(get_db)):
    """Test database connection and return table info"""
    try:
        from sqlalchemy import text
        
        # 트랜잭션 롤백 (이전 오류가 있을 경우)
        try:
            db.rollback()
        except:
            pass
        
        # 테이블 존재 확인
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = db.execute(tables_query).fetchall()
        table_names = [t[0] for t in tables]
        
        # 각 테이블의 레코드 수 확인
        counts = {}
        sample_data = {}
        
        for table in ['employee_results', 'analysis_results']:
            if table in table_names:
                try:
                    # 각 테이블마다 새로운 트랜잭션 시작
                    db.commit()
                    count_query = text(f"SELECT COUNT(*) FROM {table}")
                    count = db.execute(count_query).scalar()
                    counts[table] = count
                    
                    # 샘플 데이터 가져오기
                    if count > 0:
                        if table == 'employee_results':
                            # 컬럼 확인 쿼리
                            columns_query = text(f"""
                                SELECT column_name 
                                FROM information_schema.columns 
                                WHERE table_name = '{table}'
                            """)
                            columns = db.execute(columns_query).fetchall()
                            column_names = [c[0] for c in columns]
                            
                            sample_query = text(f"""
                                SELECT * FROM {table} 
                                LIMIT 2
                            """)
                        else:
                            sample_query = text(f"""
                                SELECT * FROM {table} 
                                LIMIT 2
                            """)
                        
                        samples = db.execute(sample_query).fetchall()
                        if samples:
                            # 컬럼 이름과 함께 샘플 데이터 저장
                            sample_data[table] = {
                                "columns": column_names if table == 'employee_results' else [],
                                "data": [dict(row._mapping) for row in samples]
                            }
                        else:
                            sample_data[table] = {"columns": [], "data": []}
                    
                    db.commit()
                    
                except Exception as e:
                    db.rollback()
                    sample_data[table] = f"Error: {str(e)}"
                    counts[table] = f"Error: {str(e)}"
        
        return {
            "status": "connected",
            "tables": table_names,
            "record_counts": counts,
            "sample_data": sample_data,
            "database_url": "Connected to Neon DB"
        }
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        try:
            db.rollback()
        except:
            pass
        return {"status": "error", "message": str(e)}

@app.get("/api/v1/employees/list")
async def get_employees_list(db: Session = Depends(get_db)):
    """Get list of all employees with AI analysis results from all tables"""
    try:
        from sqlalchemy import text
        
        # 트랜잭션 롤백 (이전 오류가 있을 경우)
        try:
            db.rollback()
        except:
            pass
        
        # 먼저 employee_results 테이블 시도
        results = []
        try:
            # employee_results 테이블 조회 (각 uid별로 최신 레코드만)
            # 서브쿼리로 각 uid의 최신 id를 먼저 찾음
            results = db.execute(text("""
                WITH latest_records AS (
                    SELECT uid, MAX(id::text) as max_id
                    FROM employee_results
                    WHERE uid IS NOT NULL
                    GROUP BY uid
                )
                SELECT 
                    er.uid,
                    er.uid as employee_id,
                    er.employee_metadata->>'name' as employee_name,
                    er.employee_metadata->>'name' as name,
                    er.employee_metadata->>'department' as department,
                    er.employee_metadata->>'position' as position,
                    er.overall_score,
                    er.overall_score as ai_score,
                    er.grade,
                    er.text_score,
                    er.quantitative_score,
                    er.confidence,
                    er.dimension_scores,
                    er.ai_feedback,
                    er.id,
                    er.job_id
                FROM employee_results er
                INNER JOIN latest_records lr ON er.uid = lr.uid AND er.id::text = lr.max_id
                WHERE er.employee_metadata->>'name' IS NOT NULL
                ORDER BY er.overall_score DESC
                LIMIT 1000
            """)).fetchall()
            logger.info(f"Found {len(results)} records from employee_results")
        except Exception as e1:
            logger.warning(f"employee_results query failed: {e1}")
            
            # analysis_results 테이블 시도 (구조가 다름)
            try:
                results = db.execute(text("""
                    SELECT DISTINCT ON (uid)
                        uid,
                        filename,
                        hybrid_score,
                        ok_grade as grade,
                        text_score,
                        quantitative_score,
                        confidence,
                        dimension_scores,
                        ai_feedback,
                        created_at,
                        id
                    FROM analysis_results
                    WHERE uid IS NOT NULL
                    ORDER BY uid, created_at DESC
                    LIMIT 1000
                """)).fetchall()
                logger.info(f"Found {len(results)} records from analysis_results")
            except Exception as e2:
                logger.error(f"All table queries failed: {e2}")
                results = []
        
        # 결과가 없으면 샘플 데이터 조회 시도
        if not results:
            logger.info("No data found, trying to fetch sample data")
            try:
                sample_query = text("""
                    SELECT * FROM employee_results 
                    LIMIT 5
                """)
                sample_results = db.execute(sample_query).fetchall()
                logger.info(f"Sample query returned {len(sample_results)} rows")
                if sample_results:
                    logger.info(f"Sample columns: {sample_results[0].keys() if hasattr(sample_results[0], 'keys') else 'N/A'}")
            except Exception as e:
                logger.error(f"Sample query failed: {e}")
        
        employees = []
        for r in results:
            # 딕셔너리로 변환 (column 이름 접근 가능하도록)
            row_dict = dict(r._mapping) if hasattr(r, '_mapping') else {}
            
            # 필드 안전하게 접근
            uid = row_dict.get('uid', '')
            name = row_dict.get('employee_name', '') or '익명'
            department = row_dict.get('department', '') or '-'
            position = row_dict.get('position', '') or '-'
            
            # 점수 처리 (overall_score 또는 hybrid_score)
            score = row_dict.get('overall_score', 0) or row_dict.get('hybrid_score', 0) or 0
            
            # Grade 계산 및 정규화
            grade = row_dict.get('grade', '') or row_dict.get('ok_grade', '')
            if not grade:
                if score >= 90: grade = "S"
                elif score >= 80: grade = "A"
                elif score >= 70: grade = "B"
                elif score >= 60: grade = "C"
                else: grade = "D"
            # OK 등급 변환
            elif grade.startswith("OK"):
                if "★★★" in grade: grade = "S"
                elif "★★" in grade: grade = "A"
                elif "★" in grade: grade = "B"
                elif "A" in grade: grade = "A"
                elif "B+" in grade: grade = "B"
                elif "B" in grade: grade = "B"
                elif "C" in grade: grade = "C"
                else: grade = "D"
            
            # 날짜 처리
            created_at = row_dict.get('created_at')
            if not created_at:
                # ID가 UUID 형태면 그걸 기준으로 날짜 추정
                created_at = None
            
            employees.append({
                "uid": uid,
                "employee_name": name,
                "department": department,
                "position": position,
                "ai_score": round(score, 1) if score else 0,
                "ai_grade": grade,
                "analysis_date": created_at.isoformat() if created_at and hasattr(created_at, 'isoformat') else None,
                "source": row_dict.get('source', 'employee_results')
            })
        
        logger.info(f"Found {len(employees)} employees from database")
        return {"employees": employees, "total": len(employees)}
    except Exception as e:
        logger.error(f"Failed to get employees list: {e}")
        # 에러 발생 시 단순 쿼리로 폴백
        try:
            simple_results = db.execute(text("""
                SELECT uid, employee_name, department, position, 
                       overall_score as ai_score, grade as ai_grade, created_at
                FROM employee_results
                WHERE uid IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 1000
            """)).fetchall()
            
            employees = []
            for r in simple_results:
                score = r.ai_score or 0
                grade = r.ai_grade or ("S" if score >= 90 else "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D")
                
                employees.append({
                    "uid": r.uid,
                    "employee_name": r.employee_name or "익명",
                    "department": r.department or "-",
                    "position": r.position or "-",
                    "ai_score": round(score, 1) if score else 0,
                    "ai_grade": grade,
                    "analysis_date": r.created_at.isoformat() if r.created_at else None,
                    "source": "employee_results"
                })
            
            return {"employees": employees, "total": len(employees)}
        except:
            return {"employees": [], "total": 0, "error": str(e)}

# Get Employee Detail API
@app.get("/api/v1/employees/{employee_uid}")
async def get_employee_detail(employee_uid: str, db: Session = Depends(get_db)):
    """Get detailed information for a specific employee"""
    try:
        from sqlalchemy import text
        
        # 여러 테이블에서 직원 정보 조회
        result = db.execute(text("""
            WITH employee_data AS (
                SELECT 
                    uid,
                    COALESCE(employee_name, employee_metadata->>'name') as employee_name,
                    COALESCE(employee_metadata->>'department', department) as department,
                    COALESCE(employee_metadata->>'position', position) as position,
                    COALESCE(overall_score, ai_score) as ai_score,
                    COALESCE(grade, ai_grade) as ai_grade,
                    text_score,
                    quantitative_score,
                    confidence,
                    dimension_scores,
                    ai_feedback,
                    created_at,
                    'employee_results' as source
                FROM employee_results
                WHERE uid = :uid
                
                UNION ALL
                
                SELECT 
                    uid,
                    metadata->>'name' as employee_name,
                    metadata->>'department' as department,
                    metadata->>'position' as position,
                    hybrid_score as ai_score,
                    ok_grade as ai_grade,
                    text_score,
                    quantitative_score,
                    confidence,
                    dimension_scores,
                    ai_feedback,
                    created_at,
                    'employee_scores' as source
                FROM employee_scores
                WHERE uid = :uid
            )
            SELECT * FROM employee_data
            ORDER BY created_at DESC
            LIMIT 1
        """), {"uid": employee_uid}).first()
        
        if not result:
            return {"error": "Employee not found", "uid": employee_uid}
        
        # Opinion 데이터 조회
        opinion_result = db.execute(text("""
            SELECT summary, key_strengths, areas_for_improvement, 
                   sentiment_score, recommendation
            FROM opinion_results
            WHERE uid = :uid
            ORDER BY created_at DESC
            LIMIT 1
        """), {"uid": employee_uid}).first()
        
        # Grade 정규화
        grade = result.ai_grade
        if grade and grade.startswith("OK"):
            if "★★★" in grade: grade = "S"
            elif "★★" in grade: grade = "A"
            elif "★" in grade: grade = "B"
            elif "A" in grade: grade = "A"
            elif "B+" in grade: grade = "B"
            elif "B" in grade: grade = "B"
            elif "C" in grade: grade = "C"
            else: grade = "D"
        
        employee_detail = {
            "uid": result.uid,
            "employee_name": result.employee_name or "익명",
            "department": result.department or "-",
            "position": result.position or "-",
            "ai_score": round(result.ai_score, 1) if result.ai_score else 0,
            "ai_grade": grade or "C",
            "text_score": round(result.text_score, 1) if result.text_score else 0,
            "quantitative_score": round(result.quantitative_score, 1) if result.quantitative_score else 0,
            "confidence": round(result.confidence * 100, 1) if result.confidence else 0,
            "dimension_scores": result.dimension_scores or {},
            "ai_feedback": result.ai_feedback or {},
            "analysis_date": result.created_at.isoformat() if result.created_at else None,
            "source": result.source
        }
        
        # Opinion 데이터 추가
        if opinion_result:
            employee_detail.update({
                "opinion_summary": opinion_result.summary,
                "key_strengths": opinion_result.key_strengths,
                "areas_for_improvement": opinion_result.areas_for_improvement,
                "sentiment_score": round(opinion_result.sentiment_score, 2) if opinion_result.sentiment_score else 0,
                "recommendation": opinion_result.recommendation
            })
        
        return employee_detail
        
    except Exception as e:
        logger.error(f"Failed to get employee detail: {e}")
        return {"error": str(e), "uid": employee_uid}

# Get Employee AI Analysis API - for detailed AI analysis view
@app.get("/api/v1/employees/{employee_uid}/ai-analysis")
async def get_employee_ai_analysis(employee_uid: str, db: Session = Depends(get_db)):
    """Get AI analysis data for employee detail view"""
    try:
        from sqlalchemy import text
        
        # 트랜잭션 롤백 (이전 오류가 있을 경우)
        try:
            db.rollback()
        except:
            pass
        
        logger.info(f"Fetching AI analysis for employee: {employee_uid}")
        
        # uid를 정수로 변환 시도 (필요한 경우)
        uid_param = employee_uid
        try:
            # 만약 uid가 숫자 문자열이면 정수로 변환
            if employee_uid.isdigit():
                uid_param = int(employee_uid)
        except:
            pass
        
        logger.info(f"Using uid parameter: {uid_param} (type: {type(uid_param).__name__})")
        
        # employee_results 테이블에서 직원 정보 조회
        # employee_metadata를 전체로 가져와서 파이썬에서 파싱
        # 여러 레코드가 있을 경우 가장 최근 것 선택 (ID 역순)
        result = db.execute(text("""
            SELECT 
                uid,
                employee_metadata,
                overall_score as ai_score,
                grade,
                dimension_scores,
                ai_feedback,
                id,
                CURRENT_TIMESTAMP as analyzed_at
            FROM employee_results
            WHERE uid = :uid
            ORDER BY id DESC
            LIMIT 1
        """), {"uid": str(employee_uid)}).first()
        
        logger.info(f"Query result for {employee_uid}: {result is not None}")
        if result:
            logger.info(f"Found record ID: {result.id}")
            logger.info(f"Score: {result.ai_score}, Grade: {result.grade}")
        
        if not result:
            # 디버깅: 실제 존재하는 uid 몇 개 확인
            sample_uids = db.execute(text("""
                SELECT uid FROM employee_results LIMIT 5
            """)).fetchall()
            logger.info(f"Sample UIDs in database: {[row.uid for row in sample_uids]}")
            logger.error(f"No data found for employee_uid: {employee_uid}")
            
            # 데이터가 없으면 에러 반환
            raise Exception(f"직원 데이터를 찾을 수 없습니다: {employee_uid}")
        
        # employee_metadata 파싱
        employee_metadata = result.employee_metadata or {}
        if isinstance(employee_metadata, str):
            import json
            try:
                employee_metadata = json.loads(employee_metadata)
            except Exception as e:
                logger.error(f"Failed to parse employee_metadata: {e}")
                employee_metadata = {}
        elif not isinstance(employee_metadata, dict):
            employee_metadata = {}
        
        # 직원 정보 추출
        employee_name = employee_metadata.get("name", "")
        employee_department = employee_metadata.get("department", "")
        employee_position = employee_metadata.get("position", "")
        
        # 이름 인코딩 문제 처리
        if employee_name and ("직원_" in employee_name or any(ord(c) > 127 and ord(c) < 256 for c in employee_name)):
            # 인코딩이 깨진 경우 직원_ID로 표시
            employee_name = f"직원_{result.uid}"
        elif not employee_name:
            employee_name = f"직원_{result.uid}"
            
        logger.info(f"Employee metadata - Name: {employee_name}, Dept: {employee_department}, Position: {employee_position}")
        
        # dimension_scores를 competencies로 변환
        competencies = result.dimension_scores or {}
        if isinstance(competencies, str):
            import json
            try:
                competencies = json.loads(competencies)
                logger.info(f"Parsed dimension_scores: {competencies}")
            except Exception as e:
                logger.error(f"Failed to parse dimension_scores: {e}")
                competencies = {}
        else:
            logger.info(f"dimension_scores type: {type(competencies)}, value: {competencies}")
        
        # 영어 키를 한글 키로 매핑
        competency_mapping = {
            "execution": "실행력",
            "growth": "성장지향",
            "collaboration": "협업",
            "customer_focus": "고객지향",
            "expertise": "전문성",
            "innovation": "혁신성",
            "leadership": "리더십",
            "communication": "커뮤니케이션",
            # 추가 가능한 매핑들
            "teamwork": "협업",
            "problem_solving": "문제해결",
            "technical": "전문성"
        }
        
        # 한글 키 정리 (실제 DB 키를 표준 8대 역량으로 매핑)
        korean_key_mapping = {
            "실행력": "실행력",
            "성장지향": "성장지향",
            "협업": "협업",
            "고객지향": "고객지향",
            "전문성": "전문성",
            "혁신성": "혁신성",
            "리더십": "리더십",
            "커뮤니케이션": "커뮤니케이션",
            # 실제 DB에 있는 키들
            "업무성과": "실행력",
            "KPI달성": "실행력",
            "태도마인드": "성장지향",
            "리더십협업": "리더십",
            "전문성학습": "전문성",
            "창의혁신": "혁신성",
            "조직적응": "협업",
            # 기타 가능한 변형들
            "리더십관리": "리더십",
            "팀플레이": "협업",
            "팀빌딩역량": "협업",
            "학습열의": "성장지향",
            "업무학습": "전문성"
        }
        
        # 실제 데이터의 키를 표준 한글 키로 변환
        korean_competencies = {}
        for key, value in competencies.items():
            # 키가 이미 한글인지 확인
            if any(ord(c) > 127 for c in key):
                # 한글 키 - 표준 키로 매핑
                standard_key = korean_key_mapping.get(key, key)
                korean_competencies[standard_key] = value
            else:
                # 영어 키 - 한글로 변환
                korean_key = competency_mapping.get(key, key)
                korean_competencies[korean_key] = value
        
        logger.info(f"Original competencies: {competencies}")
        logger.info(f"Mapped competencies: {korean_competencies}")
        
        # ai_feedback 파싱
        ai_feedback = result.ai_feedback or {}
        if isinstance(ai_feedback, str):
            import json
            try:
                ai_feedback = json.loads(ai_feedback)
                logger.info(f"Parsed ai_feedback: {ai_feedback}")
            except Exception as e:
                logger.error(f"Failed to parse ai_feedback: {e}")
                ai_feedback = {}
        else:
            logger.info(f"ai_feedback type: {type(ai_feedback)}, value: {ai_feedback}")
        
        # 강점과 개선점 추출
        strengths = []
        improvements = []
        ai_comment = ""
        
        if isinstance(ai_feedback, dict):
            strengths = ai_feedback.get("strengths", [])
            improvements = ai_feedback.get("improvements", [])
            ai_comment = ai_feedback.get("ai_feedback", ai_feedback.get("comment", ""))
            
            # 강점과 개선점이 문자열인 경우 리스트로 변환
            if isinstance(strengths, str):
                strengths = [strengths]
            if isinstance(improvements, str):
                improvements = [improvements]
        elif isinstance(ai_feedback, str):
            ai_comment = ai_feedback
        
        # 데이터가 없으면 빈 배열 반환 (목업 데이터 제거)
        if not strengths:
            strengths = []
        if not improvements:
            improvements = []
        
        # 실제 점수가 있으면 사용, 없으면 0
        final_competencies = {
            "실행력": int(korean_competencies.get("실행력", 0)),
            "성장지향": int(korean_competencies.get("성장지향", 0)),
            "협업": int(korean_competencies.get("협업", 0)),
            "고객지향": int(korean_competencies.get("고객지향", 0)),
            "전문성": int(korean_competencies.get("전문성", 0)),
            "혁신성": int(korean_competencies.get("혁신성", 0)),
            "리더십": int(korean_competencies.get("리더십", 0)),
            "커뮤니케이션": int(korean_competencies.get("커뮤니케이션", 0))
        }
        
        logger.info(f"Final competencies: {final_competencies}")
        
        # 더 풍성한 분석 데이터 생성
        competency_average = sum(final_competencies.values()) / 8
        top_competencies = sorted(final_competencies.items(), key=lambda x: x[1], reverse=True)[:3]
        low_competencies = sorted(final_competencies.items(), key=lambda x: x[1])[:3]
        
        # 성과 등급에 따른 권장사항 생성
        score = float(result.ai_score or 0)
        
        # 경력 추천 생성
        career_recommendations = []
        if score >= 80:
            career_recommendations = [
                "리더십 역할 확장 - 팀 관리 및 멘토링 역할 기회",
                "전략 기획 참여 - 조직 발전 방향 수립 참여",
                "교차 기능 프로젝트 리드 - 다부서 협업 프로젝트 주도"
            ]
        elif score >= 60:
            career_recommendations = [
                "전문성 심화 - 현재 업무 영역의 전문가로 성장",
                "프로젝트 관리 역량 개발 - 중규모 프로젝트 담당",
                "팀 내 핵심 업무 담당 - 중요 업무 책임 확대"
            ]
        else:
            career_recommendations = [
                "기본 업무 역량 강화 - 현재 업무의 완성도 향상",
                "멘토링 프로그램 참여 - 선배 직원과의 1:1 멘토링",
                "기초 스킬 개발 - 업무 필수 역량 집중 개발"
            ]
        
        # 교육 추천 생성
        education_suggestions = []
        for comp_name, comp_score in low_competencies:
            if comp_score < 60:
                if comp_name == "리더십":
                    education_suggestions.append("리더십 스킬 향상 교육 - 팀 관리 및 의사결정 역량")
                elif comp_name == "커뮤니케이션":
                    education_suggestions.append("커뮤니케이션 스킬 교육 - 효과적인 의사소통 기법")
                elif comp_name == "협업":
                    education_suggestions.append("팀워크 강화 교육 - 협업 및 갈등 관리 기법")
                elif comp_name == "혁신성":
                    education_suggestions.append("창의적 사고 교육 - 혁신과 변화 관리")
                elif comp_name == "전문성":
                    education_suggestions.append("전문 기술 교육 - 업무 관련 전문성 강화")
                else:
                    education_suggestions.append(f"{comp_name} 역량 강화 프로그램")
        
        # 기본 교육 프로그램 추가
        if not education_suggestions:
            education_suggestions = [
                "리더십 역량 강화 프로그램",
                "디지털 전환 대응 교육",
                "업무 생산성 향상 교육"
            ]
        
        # 성과 분석 지표 생성
        performance_indicators = {
            "overall_ranking": f"상위 {100 - min(95, max(5, int(score/10)*10))}%",
            "competency_balance": "균형" if max(final_competencies.values()) - min(final_competencies.values()) <= 20 else "편중",
            "growth_potential": "높음" if score >= 80 else "보통" if score >= 60 else "개발필요",
            "risk_level": "낮음" if score >= 70 else "보통" if score >= 50 else "높음",
            "leadership_readiness": "준비됨" if final_competencies.get("리더십", 0) >= 70 and score >= 75 else "개발필요"
        }
        
        # 부서/직급 정보 강화
        department_display = employee_department if employee_department and employee_department != "" else "부서 정보 없음"
        position_display = employee_position if employee_position and employee_position != "" else "직급 정보 없음"
        
        # 근무 경력 추정 (점수 기반)
        estimated_experience = "5년 이상" if score >= 80 else "3-5년" if score >= 60 else "1-3년"
        
        # 종합 피드백 생성 (AI 코멘트가 없을 경우)
        if not ai_comment:
            ai_comment = f"""
{employee_name}님은 현재 {score}점의 AI 종합 점수를 받으며, 전체적으로 {'우수한' if score >= 80 else '양호한' if score >= 60 else '개발이 필요한'} 성과를 보이고 있습니다.

특히 {top_competencies[0][0]}({top_competencies[0][1]}점) 영역에서 뛰어난 역량을 보여주고 있으며, 
{top_competencies[1][0]}({top_competencies[1][1]}점)와 {top_competencies[2][0]}({top_competencies[2][1]}점) 분야에서도 
강점을 나타내고 있습니다.

향후 {low_competencies[0][0]}({low_competencies[0][1]}점) 영역의 집중 개발을 통해 
더욱 균형 잡힌 역량 발전이 기대됩니다.
            """.strip()
        
        return {
            "employee_id": result.uid,
            "name": employee_name,
            "department": department_display,
            "position": position_display,
            "ai_score": round(score),
            "grade": result.grade or "C",
            "competencies": final_competencies,
            "competency_average": round(competency_average, 1),
            "top_competencies": top_competencies,
            "low_competencies": low_competencies,
            "strengths": strengths[:5] if strengths else [f"{top_competencies[0][0]} 역량이 뛰어남", f"{top_competencies[1][0]} 분야 우수 성과"],
            "improvements": improvements[:3] if improvements else [f"{low_competencies[0][0]} 역량 개발 필요", f"{low_competencies[1][0]} 영역 집중 강화"],
            "ai_comment": ai_comment,
            "career_recommendation": career_recommendations[:4],
            "education_suggestion": education_suggestions[:4],
            "performance_indicators": performance_indicators,
            "estimated_experience": estimated_experience,
            "analyzed_at": result.analyzed_at.isoformat() if result.analyzed_at else None,
            "analysis_version": "AIRISS v5.0 Enhanced"
        }
        
    except Exception as e:
        logger.error(f"Failed to get employee AI analysis for {employee_uid}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {e.args if hasattr(e, 'args') else 'No details'}")
        
        # 에러 발생시 에러 메시지 반환
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"직원 데이터를 찾을 수 없습니다: {employee_uid}")

# Debug Test Page
@app.get("/debug")
async def debug_test():
    """Debug test page for API testing"""
    from fastapi.responses import Response
    
    filepath = os.path.join(os.path.dirname(__file__), "templates", "debug_test.html")
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content=content, media_type="text/html; charset=utf-8")
    
    return {"error": "Debug test page not found"}

# API Test Page for Employee Details
@app.get("/api-test")
async def api_test():
    """API test page for employee detail debugging"""
    from fastapi.responses import Response
    
    filepath = os.path.join(os.path.dirname(__file__), "templates", "api_test.html")
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content=content, media_type="text/html; charset=utf-8")
    
    return {"error": "API test page not found"}

# AIRISS v5.0 Test Dashboard - Debug version
@app.get("/test")
async def airiss_v5_test():
    """AIRISS v5.0 Test Dashboard for debugging"""
    from fastapi.responses import Response
    
    filepath = os.path.join(os.path.dirname(__file__), "templates", "airiss_v5_test.html")
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content=content, media_type="text/html; charset=utf-8")
    
    return {"error": "Test dashboard not found"}

# Responsive Layout Test Page
@app.get("/responsive-test")
async def responsive_test():
    """Responsive layout test page"""
    from fastapi.responses import Response
    
    filepath = os.path.join(os.path.dirname(__file__), "templates", "responsive_test.html")
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content=content, media_type="text/html; charset=utf-8")
    
    return {"error": "Responsive test page not found"}

# AIRISS v5.0 Dashboard - Legacy route (kept for backward compatibility)
# Note: Main dashboard is now served at root "/" for MSA integration
@app.get("/hr")
async def airiss_v5_dashboard():
    """AIRISS v5.0 Dashboard - Legacy route (redirects to main)"""
    from fastapi.responses import Response
    import random
    
    filepath = os.path.join(os.path.dirname(__file__), "templates", "airiss_v5.html")
    
    if not os.path.exists(filepath):
        return {"error": "AIRISS v5.0 dashboard not found", "path": filepath}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 버전 정보와 빌드 타임스탬프 주입
    timestamp = datetime.now().isoformat()
    build_id = random.randint(1000, 9999)
    
    # 메타 태그 업데이트
    content = content.replace('content="2025-08-07"', f'content="{timestamp}"')
    content = content.replace('v5.0.0-2025.08.07', f'v5.0.0-{build_id}')
    
    return Response(
        content=content,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache", 
            "Expires": "0",
            "X-Version": f"5.0.0-{build_id}",
            "X-Build-Time": timestamp,
            "X-System": "AIRISS-v5.0"
        }
    )

# COMPLETELY NEW ENDPOINT - Never cached before
@app.get("/dashboard/latest")
async def dashboard_latest():
    """Brand new dashboard endpoint"""
    from fastapi.responses import Response
    
    filepath = os.path.join(os.path.dirname(__file__), "templates", "dashboard_latest.html")
    
    if not os.path.exists(filepath):
        # 파일이 없으면 직접 HTML 생성
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dashboard Latest - {datetime.now().isoformat()}</title>
        </head>
        <body>
            <h1>최신 대시보드 - 직접 생성</h1>
            <p>생성 시간: {datetime.now().isoformat()}</p>
            <p>파일 경로: {filepath}</p>
            <p>파일 존재: False</p>
        </body>
        </html>
        """
        return Response(content=html, media_type="text/html")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 타임스탬프 주입
    content = content.replace("</body>", f"<script>console.log('Served at: {datetime.now().isoformat()}')</script></body>")
    
    return Response(
        content=content,
        media_type="text/html",
        headers={
            "Cache-Control": "no-store",
            "X-Accel-Expires": "0"
        }
    )

# Simple test to check which files exist
@app.get("/api/check-files")
async def check_files():
    """Simple file check"""
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    files = {}
    
    for filename in ["hr_dashboard_2025_01_07.html", "hr_dashboard_v3.html", "hr_dashboard_v2.html"]:
        filepath = os.path.join(templates_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                title_line = "Not found"
                for line in lines[:10]:
                    if "<title>" in line:
                        title_line = line.strip()
                        break
            files[filename] = {"exists": True, "title": title_line}
        else:
            files[filename] = {"exists": False}
    
    return files

# Test endpoint to verify file content
@app.get("/api/test-file-content")
async def test_file_content():
    """Check actual file content on server"""
    try:
        import re
        from datetime import datetime
        
        template_path = os.path.join(os.path.dirname(__file__), "templates", "hr_dashboard_2025_01_07.html")
        
        result = {
            "file_exists": os.path.exists(template_path),
            "file_path": template_path,
        }
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 처음 500자와 title 태그 찾기
                result["first_500_chars"] = content[:500]
                
                # title 태그 내용 찾기
                title_match = re.search(r'<title>(.*?)</title>', content)
                if title_match:
                    result["title_tag"] = title_match.group(1)
                
                result["file_size"] = len(content)
                
                # 파일 수정 시간
                result["last_modified"] = datetime.fromtimestamp(os.path.getmtime(template_path)).isoformat()
        
        return result
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

# API-based HR Dashboard - FORCE NEW VERSION
@app.get("/api/hr-dashboard-html")
async def api_hr_dashboard():
    """Serve HR Dashboard as API response - FORCE READ FROM FILE"""
    from fastapi.responses import Response
    import hashlib
    
    # ALWAYS read the 2025 version
    template_path = os.path.join(os.path.dirname(__file__), "templates", "hr_dashboard_2025_01_07.html")
    
    if not os.path.exists(template_path):
        return {"error": "File not found", "path": template_path}
    
    # Force fresh read every time
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Generate unique response each time
    import random
    timestamp = datetime.now().isoformat()
    unique_id = random.randint(1000, 9999)
    
    # Inject timestamp into HTML to prevent any caching
    html_content = html_content.replace(
        "</title>",
        f" - {timestamp}</title>"
    )
    
    # Return with strict no-cache headers
    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Timestamp": timestamp,
            "X-Unique-ID": str(unique_id),
            "X-File": "hr_dashboard_2025_01_07.html"
        }
    )

# Register all API routers
try:
    from app.api.v1.endpoints.analysis import router as analysis_router
    app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["Analysis"])
    logger.info("Analysis router registered")
except ImportError as e:
    logger.error(f"Failed to import analysis router: {e}")

try:
    from app.api.v1.endpoints.files import router as files_router
    app.include_router(files_router, prefix="/api/v1/files", tags=["Files"])
    logger.info("Files router registered")
except ImportError as e:
    logger.error(f"Failed to import files router: {e}")

try:
    from app.api.v1.endpoints.upload import router as upload_router
    app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
    logger.info("Upload router registered")
except ImportError as e:
    logger.error(f"Failed to import upload router: {e}")

try:
    from app.api.v1.endpoints.websocket import router as websocket_router
    app.include_router(websocket_router, tags=["WebSocket"])
    logger.info("WebSocket router registered")
except ImportError as e:
    logger.error(f"Failed to import websocket router: {e}")

try:
    from app.api.v1.endpoints.health import router as health_router
    app.include_router(health_router, prefix="/api/v1", tags=["Health"])
    logger.info("Health router registered")
except ImportError as e:
    logger.error(f"Failed to import health router: {e}")

try:
    from app.api.v1.endpoints.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
    logger.info("Dashboard router registered")
except ImportError as e:
    logger.error(f"Failed to import dashboard router: {e}")

# v4.2 Employee AI Analysis endpoints
try:
    from app.api.v1.endpoints.employees import router as employees_router
    app.include_router(employees_router, prefix="/api/v1/employees", tags=["Employees"])
    logger.info("Employees router registered - v4.2 AI Dashboard")
except ImportError as e:
    logger.error(f"Failed to import employees router: {e}")

# Opinion Analysis endpoints
try:
    from app.api.v1.endpoints.analysis_opinion import router as opinion_router
    app.include_router(opinion_router, prefix="/api/v1/analysis", tags=["Opinion Analysis"])
    logger.info("Opinion Analysis router registered")
except ImportError as e:
    logger.error(f"Failed to import opinion analysis router: {e}")

# Configuration endpoints
try:
    from app.api.v1.endpoints.config import router as config_router
    app.include_router(config_router, prefix="/api/v1/config", tags=["Configuration"])
    logger.info("Configuration router registered")
except ImportError as e:
    logger.error(f"Failed to import config router: {e}")

# HR Dashboard endpoints
try:
    from app.api.v1.endpoints.hr_dashboard import router as hr_dashboard_router
    app.include_router(hr_dashboard_router, prefix="/api/v1/hr-dashboard", tags=["HR Dashboard"])
    logger.info("HR Dashboard router registered")
except ImportError as e:
    logger.error(f"Failed to import HR dashboard router: {e}")

# OpenAI Proxy endpoints (Railway 환경용)
try:
    from app.api.v1.endpoints.openai_proxy import router as proxy_router
    app.include_router(proxy_router, prefix="/api/v1", tags=["OpenAI Proxy"])
    logger.info("OpenAI Proxy router registered - Railway 연결 문제 해결용")
except ImportError as e:
    logger.error(f"Failed to import OpenAI proxy router: {e}")

# Static file serving
# Use absolute path for Windows
base_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.getenv("REACT_BUILD_PATH", os.path.join(base_dir, "static"))

# Mount static directories
if os.path.exists(static_path):
    # Mount static subdirectory
    static_files_path = os.path.join(static_path, "static")
    if os.path.exists(static_files_path):
        app.mount("/static", StaticFiles(directory=static_files_path), name="static")
        logger.info(f"✅ Mounted /static from: {static_files_path}")
    
    # Mount other static directories directly
    for subdir in ["css", "js", "fonts"]:
        subdir_path = os.path.join(static_path, subdir)
        if os.path.exists(subdir_path):
            app.mount(f"/{subdir}", StaticFiles(directory=subdir_path), name=subdir)
            logger.info(f"✅ Mounted /{subdir} from: {subdir_path}")
    
    logger.info(f"✅ Static files configured from: {static_path}")
else:
    logger.warning(f"⚠️ Static path not found: {static_path}")

# HR Dashboard route - MUST BE BEFORE CATCH-ALL
@app.get("/hr-dashboard")
async def serve_hr_dashboard():
    """Serve HR Dashboard page"""
    import random
    from fastapi.responses import FileResponse, JSONResponse
    
    # 디버깅을 위한 파일 체크
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    available_files = []
    
    # v3 파일 우선 사용
    v3_path = os.path.join(templates_dir, "hr_dashboard_v3.html")
    if os.path.exists(v3_path):
        available_files.append("v3 exists")
        response = FileResponse(v3_path)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["X-Version"] = f"v3-{random.randint(1000, 9999)}"
        response.headers["X-File-Served"] = "hr_dashboard_v3.html"
        logger.info(f"Serving: hr_dashboard_v3.html from {v3_path}")
        return response
    
    # v2 fallback
    v2_path = os.path.join(templates_dir, "hr_dashboard_v2.html")
    if os.path.exists(v2_path):
        available_files.append("v2 exists")
        response = FileResponse(v2_path)
        response.headers["X-File-Served"] = "hr_dashboard_v2.html"
        logger.info(f"Serving: hr_dashboard_v2.html from {v2_path}")
        return response
    
    # Return debug info
    return JSONResponse({
        "message": "HR Dashboard not found",
        "templates_dir": templates_dir,
        "available_files": available_files,
        "v3_path": v3_path,
        "v2_path": v2_path
    })

# NEW DASHBOARD - Completely new path to bypass all caching
@app.get("/hr-new")
async def serve_hr_new():
    """New HR Dashboard with unique filename"""
    from fastapi.responses import FileResponse
    new_path = os.path.join(os.path.dirname(__file__), "templates", "hr_dashboard_2025_01_07.html")
    if os.path.exists(new_path):
        response = FileResponse(new_path)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    return {"error": "new dashboard not found", "path": new_path}

# Direct v3 access for testing
@app.get("/hr-v3")
async def serve_hr_v3():
    """Direct access to v3 dashboard"""
    from fastapi.responses import FileResponse
    v3_path = os.path.join(os.path.dirname(__file__), "templates", "hr_dashboard_v3.html")
    if os.path.exists(v3_path):
        response = FileResponse(v3_path)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
    return {"error": "v3 not found", "path": v3_path}

# Debug endpoint to check which file is being served
@app.get("/hr-dashboard-debug")
async def debug_hr_dashboard():
    """Debug endpoint to check template files"""
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    files = []
    
    if os.path.exists(templates_dir):
        for f in os.listdir(templates_dir):
            if "hr_dashboard" in f:
                file_path = os.path.join(templates_dir, f)
                file_size = os.path.getsize(file_path)
                with open(file_path, 'r', encoding='utf-8') as file:
                    first_line = file.readline()
                    for _ in range(5):
                        line = file.readline()
                        if '<title>' in line:
                            title = line.strip()
                            break
                    else:
                        title = "No title found"
                
                files.append({
                    "name": f,
                    "size": file_size,
                    "title": title,
                    "path": file_path
                })
    
    return {
        "templates_dir": templates_dir,
        "files": files,
        "current_working_dir": os.getcwd()
    }

# HR Dashboard Simple Test route
@app.get("/hr-dashboard-test")
async def serve_hr_dashboard_test():
    """Serve HR Dashboard Test page for debugging"""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "hr_dashboard_simple.html")
    if os.path.exists(template_path):
        return FileResponse(template_path)
    return {"message": "HR Dashboard Test not found"}

# Executive Dashboard route (alternative path)
@app.get("/executive-dashboard")
async def serve_executive_dashboard():
    """Serve Executive Dashboard page (alternative path)"""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "hr_dashboard.html")
    if os.path.exists(template_path):
        return FileResponse(template_path)
    return {"message": "Executive Dashboard not found"}

# ============================================================================
# AIRISS 분석결과 API - 외부 시스템 연동용
# ============================================================================

@app.get("/api/v1/airiss/talent-analysis")
async def get_talent_analysis(db: Session = Depends(get_db)):
    """핵심인재, 승진후보군 등 인재풀 분석 결과 제공"""
    try:
        from app.models.employee import Employee
        from sqlalchemy import func
        
        # 전체 직원 데이터 조회
        employees = db.query(Employee).all()
        
        if not employees:
            return {"message": "No employee data found", "data": []}
        
        # 인재 분류 로직
        talent_pools = {
            "core_talent": [],      # 핵심인재 (S, A+)
            "promotion_candidates": [],  # 승진후보 (A+, A)
            "high_performers": [],  # 우수인재 (A)
            "development_needed": [], # 개발필요 (B+, B)
            "at_risk": []          # 위험인재 (C, D)
        }
        
        for emp in employees:
            grade = emp.ai_grade or emp.grade or emp.OK등급 or 'C'
            score = emp.ai_score or emp.overall_score or emp.AIRISS_v2_종합점수 or 0
            
            emp_data = {
                "employee_id": emp.uid,
                "name": emp.name or emp.이름,
                "department": emp.department or emp.부서,
                "position": emp.position or emp.직급,
                "grade": grade,
                "score": score,
                "years_of_service": getattr(emp, 'years_of_service', None) or getattr(emp, '근속년수', 0),
                "last_evaluation": emp.updated_at.strftime('%Y-%m-%d') if emp.updated_at else None
            }
            
            # 인재풀 분류
            if grade in ['S', 'A+']:
                talent_pools["core_talent"].append(emp_data)
                if grade == 'A+' or score >= 850:  # 승진 가능 점수
                    talent_pools["promotion_candidates"].append(emp_data)
            elif grade == 'A':
                talent_pools["high_performers"].append(emp_data)
                if score >= 800:  # 승진 후보 기준
                    talent_pools["promotion_candidates"].append(emp_data)
            elif grade in ['B+', 'B']:
                talent_pools["development_needed"].append(emp_data)
            else:  # C, D
                talent_pools["at_risk"].append(emp_data)
        
        # 요약 통계
        summary = {
            "total_employees": len(employees),
            "core_talent_count": len(talent_pools["core_talent"]),
            "promotion_candidates_count": len(talent_pools["promotion_candidates"]),
            "high_performers_count": len(talent_pools["high_performers"]),
            "development_needed_count": len(talent_pools["development_needed"]),
            "at_risk_count": len(talent_pools["at_risk"]),
            "talent_density": round((len(talent_pools["core_talent"]) / len(employees)) * 100, 2),
            "analysis_date": datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return {
            "status": "success",
            "summary": summary,
            "talent_pools": talent_pools
        }
        
    except Exception as e:
        logger.error(f"Error in talent analysis API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/airiss/department-performance")
async def get_department_performance(db: Session = Depends(get_db)):
    """부서별 성과 분석 결과 제공"""
    try:
        from app.models.employee import Employee
        
        employees = db.query(Employee).all()
        
        if not employees:
            return {"message": "No employee data found", "departments": []}
        
        # 부서별 데이터 집계
        dept_data = {}
        
        for emp in employees:
            dept = emp.department or emp.부서 or '미지정'
            grade = emp.ai_grade or emp.grade or emp.OK등급 or 'C'
            score = emp.ai_score or emp.overall_score or emp.AIRISS_v2_종합점수 or 0
            
            if dept not in dept_data:
                dept_data[dept] = {
                    "department": dept,
                    "total_employees": 0,
                    "total_score": 0,
                    "grades": {'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0},
                    "employees": []
                }
            
            dept_data[dept]["total_employees"] += 1
            dept_data[dept]["total_score"] += score
            dept_data[dept]["grades"][grade] += 1
            
            dept_data[dept]["employees"].append({
                "employee_id": emp.uid,
                "name": emp.name or emp.이름,
                "position": emp.position or emp.직급,
                "grade": grade,
                "score": score
            })
        
        # 부서별 성과 계산
        departments = []
        for dept, data in dept_data.items():
            avg_score = round(data["total_score"] / data["total_employees"]) if data["total_employees"] > 0 else 0
            core_talent = data["grades"]["S"] + data["grades"]["A+"]
            
            dept_performance = {
                "department": dept,
                "total_employees": data["total_employees"],
                "average_score": avg_score,
                "core_talent_count": core_talent,
                "talent_ratio": round((core_talent / data["total_employees"]) * 100, 2) if data["total_employees"] > 0 else 0,
                "grade_distribution": data["grades"],
                "performance_level": "우수" if avg_score >= 750 else "보통" if avg_score >= 650 else "개선필요",
                "employees": data["employees"]
            }
            
            departments.append(dept_performance)
        
        # 성과순으로 정렬
        departments.sort(key=lambda x: x["average_score"], reverse=True)
        
        return {
            "status": "success",
            "analysis_date": datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S'),
            "total_departments": len(departments),
            "departments": departments
        }
        
    except Exception as e:
        logger.error(f"Error in department performance API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/airiss/risk-analysis")
async def get_risk_analysis(db: Session = Depends(get_db)):
    """위험인재 및 리스크 분석 결과 제공"""
    try:
        from app.models.employee import Employee
        
        employees = db.query(Employee).all()
        
        if not employees:
            return {"message": "No employee data found", "risk_analysis": {}}
        
        # 위험도 분석
        risk_categories = {
            "high_risk": [],     # 고위험 (D, 저성과 C)
            "medium_risk": [],   # 중위험 (C)
            "low_risk": [],      # 저위험 (B, B+)
            "retention_candidates": []  # 리텐션 대상 (우수 인재 중 위험 요소)
        }
        
        total_score = 0
        grade_distribution = {'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for emp in employees:
            grade = emp.ai_grade or emp.grade or emp.OK등급 or 'C'
            score = emp.ai_score or emp.overall_score or emp.AIRISS_v2_종합점수 or 0
            total_score += score
            grade_distribution[grade] += 1
            
            emp_data = {
                "employee_id": emp.uid,
                "name": emp.name or emp.이름,
                "department": emp.department or emp.부서,
                "position": emp.position or emp.직급,
                "grade": grade,
                "score": score,
                "risk_factors": []
            }
            
            # 위험 요소 분석
            if grade == 'D':
                emp_data["risk_factors"].extend(["극저성과", "즉시개선필요"])
                risk_categories["high_risk"].append(emp_data)
            elif grade == 'C':
                if score < 500:
                    emp_data["risk_factors"].append("고위험성과")
                    risk_categories["high_risk"].append(emp_data)
                else:
                    emp_data["risk_factors"].append("성과개선필요")
                    risk_categories["medium_risk"].append(emp_data)
            elif grade in ['B', 'B+']:
                emp_data["risk_factors"].append("개발필요")
                risk_categories["low_risk"].append(emp_data)
            elif grade in ['S', 'A+', 'A']:
                # 우수 인재 중 리텐션 고려 대상 (임의 기준)
                years_service = getattr(emp, 'years_of_service', None) or getattr(emp, '근속년수', 0)
                if years_service and years_service > 10:
                    emp_data["risk_factors"].append("장기근속우수인재")
                    risk_categories["retention_candidates"].append(emp_data)
        
        # 전체 리스크 평가
        total_employees = len(employees)
        high_risk_rate = round((len(risk_categories["high_risk"]) / total_employees) * 100, 2)
        avg_score = round(total_score / total_employees) if total_employees > 0 else 0
        
        risk_level = "HIGH" if high_risk_rate > 20 else "MEDIUM" if high_risk_rate > 10 else "LOW"
        
        risk_summary = {
            "total_employees": total_employees,
            "average_score": avg_score,
            "overall_risk_level": risk_level,
            "high_risk_count": len(risk_categories["high_risk"]),
            "medium_risk_count": len(risk_categories["medium_risk"]),
            "low_risk_count": len(risk_categories["low_risk"]),
            "retention_candidates_count": len(risk_categories["retention_candidates"]),
            "high_risk_rate": high_risk_rate,
            "grade_distribution": grade_distribution,
            "recommendations": []
        }
        
        # 권고사항 생성
        if high_risk_rate > 20:
            risk_summary["recommendations"].append("즉시 성과 개선 계획 수립 필요")
        if len(risk_categories["retention_candidates"]) > 0:
            risk_summary["recommendations"].append("핵심 인재 리텐션 전략 강화")
        if avg_score < 650:
            risk_summary["recommendations"].append("전사 교육 및 개발 프로그램 확대")
        
        return {
            "status": "success",
            "analysis_date": datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S'),
            "risk_summary": risk_summary,
            "risk_categories": risk_categories
        }
        
    except Exception as e:
        logger.error(f"Error in risk analysis API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/v1/airiss/export/csv")
async def export_analysis_csv(analysis_type: str = "talent", db: Session = Depends(get_db)):
    """AIRISS 분석결과를 CSV 형태로 내보내기"""
    try:
        from fastapi.responses import StreamingResponse
        import csv
        import io
        
        from app.models.employee import Employee
        employees = db.query(Employee).all()
        
        if not employees:
            raise HTTPException(status_code=404, detail="No employee data found")
        
        # CSV 생성
        output = io.StringIO()
        
        if analysis_type == "talent":
            writer = csv.writer(output)
            writer.writerow(['직원ID', '이름', '부서', '직급', '등급', '점수', '인재분류', '분석일시'])
            
            for emp in employees:
                grade = emp.ai_grade or emp.grade or emp.OK등급 or 'C'
                score = emp.ai_score or emp.overall_score or emp.AIRISS_v2_종합점수 or 0
                
                # 인재 분류
                if grade in ['S', 'A+']:
                    talent_type = '핵심인재'
                elif grade == 'A':
                    talent_type = '우수인재'
                elif grade in ['B+', 'B']:
                    talent_type = '개발필요'
                else:
                    talent_type = '위험인재'
                
                writer.writerow([
                    emp.uid,
                    emp.name or emp.이름,
                    emp.department or emp.부서,
                    emp.position or emp.직급,
                    grade,
                    score,
                    talent_type,
                    datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type='text/csv',
            headers={
                "Content-Disposition": f"attachment; filename=airiss_{analysis_type}_{datetime.now(KST).strftime('%Y%m%d')}.csv"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in CSV export API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Serve AIRISS v5.0 Dashboard as main page - MSA integration for EHR
@app.get("/")
async def serve_root():
    """Serve AIRISS v5.0 Dashboard for root path - MSA integrated version"""
    from fastapi.responses import Response
    import time
    
    # AIRISS v5.0 대시보드를 메인으로 서빙
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, "templates", "airiss_v5.html")
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 버전 태그를 동적으로 추가하여 캐시 무효화
        timestamp = int(time.time())
        content = content.replace('</title>', f' - v{timestamp}</title>')
        
        # 캐싱 완전 방지를 위한 헤더 설정
        return Response(
            content=content,
            media_type="text/html; charset=utf-8",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0, private",
                "Pragma": "no-cache",
                "Expires": "0",
                "X-Content-Type-Options": "nosniff",
                "X-Version": f"5.0.3-{timestamp}",
                "Clear-Site-Data": '"cache"'
            }
        )
    
    # Fallback: React 앱이 있으면 서빙 (하위 호환성)
    if os.path.exists(static_path):
        index_path = os.path.join(static_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
    
    return {"message": "AIRISS v5.0 API - HR Analysis System"}

# Catch-all for React Router - MUST BE ABSOLUTE LAST
@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    """Catch-all route for React SPA"""
    # Skip if it's an API route or WebSocket
    if full_path.startswith("api/") or full_path.startswith("ws"):
        # Return 404 for undefined API routes
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Skip HR dashboard routes - IMPORTANT
    if full_path.startswith("hr-") or full_path == "hr":
        # Let the specific hr- routes handle these
        raise HTTPException(status_code=404, detail="Not a React route")
    
    # Skip specific routes that have their own handlers
    # hr-dashboard는 위에서 처리되므로 여기서 제외하지 않음
    if full_path in ["docs", "redoc", "openapi.json"]:
        raise HTTPException(status_code=404, detail="Not found")
    
    # Check if static path exists
    if not os.path.exists(static_path):
        raise HTTPException(status_code=404, detail="Static files not found")
    
    # Try to serve the exact file if it exists
    file_path = os.path.join(static_path, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Otherwise serve index.html for client-side routing
    index_path = os.path.join(static_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting AIRISS v4.0 server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)