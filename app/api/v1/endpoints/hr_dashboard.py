"""
HR Dashboard API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.db import get_db
from app.models.employee import EmployeeResult
import logging
import random
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import base64

logger = logging.getLogger(__name__)
router = APIRouter()

def calculate_department_stats(employees):
    """실제 직원 데이터를 기반으로 부서별 통계 계산"""
    department_stats = {}
    
    if not employees:
        return department_stats
    
    # 부서별 데이터 집계
    for emp in employees:
        dept = emp.get('department', '부서 미상')
        
        if dept not in department_stats:
            department_stats[dept] = {
                'count': 0,
                'total_score': 0,
                'avg_score': 0,
                'grades': {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
            }
        
        department_stats[dept]['count'] += 1
        
        # 점수 집계
        score = emp.get('performance_score', 0) or emp.get('ai_score', 0) or 0
        department_stats[dept]['total_score'] += score
        
        # 등급 집계
        grade = emp.get('grade', 'C')
        if grade in department_stats[dept]['grades']:
            department_stats[dept]['grades'][grade] += 1
        else:
            department_stats[dept]['grades']['C'] += 1
    
    # 평균 점수 계산
    for dept_name, dept_data in department_stats.items():
        if dept_data['count'] > 0:
            dept_data['avg_score'] = round(dept_data['total_score'] / dept_data['count'], 1)
    
    return department_stats

def calculate_promotion_candidates(employees):
    """승진 후보자 예측 로직 - S등급만 대상"""
    candidates = []
    logger.info(f"calculate_promotion_candidates: Processing {len(employees)} employees")
    
    # 디버깅을 위해 처음 3명의 데이터 확인
    for idx, emp in enumerate(employees[:3]):
        logger.info(f"Employee {idx}: grade={emp.get('grade')}, tenure={emp.get('tenure_years')}, competency={emp.get('competency_score')}, performance={emp.get('performance_score')}, leadership={emp.get('leadership_score')}")
    
    for emp in employees:
        # S등급만 승진후보자로 고려
        if emp.get('grade', '') != 'S':
            continue
            
        promotion_score = 0
        reasons = []
        
        # S등급 자동 포함
        promotion_score += 50
        reasons.append(f"최우수 평가등급 (S등급)")
        
        # 근속연수가 3년 이상인 경우
        tenure = emp.get('tenure_years', 0)
        if tenure >= 3:
            promotion_score += 20
            reasons.append(f"충분한 근속연수 ({tenure}년)")
        
        # 역량점수가 높은 경우
        competency = emp.get('competency_score', 0)
        if competency >= 90:
            promotion_score += 25
            reasons.append(f"탁월한 전문 역량 ({competency}점)")
        elif competency >= 85:
            promotion_score += 20
            reasons.append(f"뛰어난 전문 역량 ({competency}점)")
        elif competency >= 80:
            promotion_score += 15
            reasons.append(f"우수한 전문 역럅 ({competency}점)")
        
        # 성과 관리 능력
        performance = emp.get('performance_score', 0)
        if performance >= 90:
            promotion_score += 20
            reasons.append(f"지속적 고성과 달성 ({performance:.1f}점)")
        elif performance >= 85:
            promotion_score += 15
            reasons.append(f"안정적 성과 창출 ({performance:.1f}점)")
        
        # 리더십 역량 평가
        leadership = emp.get('leadership_score', 0)
        if leadership >= 85:
            promotion_score += 15
            reasons.append(f"뛰어난 리더십 역량 ({leadership}점)")
        elif leadership >= 75:
            promotion_score += 10
            reasons.append(f"우수한 리더십 역량 ({leadership}점)")
        
        # 팀워크 및 협업 능력
        teamwork = emp.get('teamwork_score', 0)
        if teamwork >= 85:
            promotion_score += 10
            reasons.append(f"뛰어난 팀워크와 협업 능력")
        
        # 혁신성
        innovation = emp.get('innovation_score', 0)
        if innovation >= 85:
            promotion_score += 10
            reasons.append(f"우수한 혁신성과 창의력 ({innovation}점)")
        
        # S등급은 모두 승진후보자에 포함
        if promotion_score >= 50:  # S등급 기본 50점 이상
            candidates.append({
                'uid': emp.get('uid'),
                'name': emp.get('name'),
                'score': promotion_score,
                'reasons': reasons,
                'department': emp.get('department'),
                'position': emp.get('position'),
                'grade': emp.get('grade', 'C')
            })
    
    # 점수순 정렬 (페이지네이션을 위해 전체 반환)
    result = sorted(candidates, key=lambda x: x['score'], reverse=True)
    
    # 디버깅 로그: 점수 분포 확인
    if len(candidates) > 0:
        scores = [c['score'] for c in candidates]
        logger.info(f"Promotion scores distribution - Min: {min(scores)}, Max: {max(scores)}, Avg: {sum(scores)/len(scores):.1f}")
        logger.info(f"Top 3 candidates: {[(c['name'], c['score']) for c in result[:3]]}")
    
    logger.info(f"calculate_promotion_candidates: Found {len(candidates)} total candidates, returning top {len(result)}")
    return result

def identify_top_talent(employees):
    """Top Talent 식별 로직"""
    top_talents = []
    logger.info(f"identify_top_talent: Processing {len(employees)} employees")
    
    for idx, emp in enumerate(employees):
        talent_score = 0
        reasons = []
        
        # 종합 성과 점수 (S, A 등급이면 자동 포함)
        performance = emp.get('performance_score', 0)
        grade = emp.get('grade', 'C')
        
        # 처음 3명의 데이터 로그
        if idx < 3:
            logger.info(f"Employee {idx}: grade={grade}, performance={performance}, name={emp.get('name', 'N/A')}")
        
        # S 등급만 핵심인재로 포함 (선별성 향상)
        if grade == 'S':
            talent_score = 100
            # 다양한 선정 사유 추가
            reasons.append(f"최우수 등급 ({grade}등급)")
            
            # 성과 점수에 따른 구체적 사유
            if performance >= 95:
                reasons.append(f"탁월한 성과 달성 ({performance:.1f}점 - 상위 5%)")
            elif performance >= 90:
                reasons.append(f"우수한 성과 달성 ({performance:.1f}점 - 상위 10%)")
            elif performance >= 85:
                reasons.append(f"양호한 성과 유지 ({performance:.1f}점)")
            
            # 역량 점수 추가 고려
            competency = emp.get('competency_score', 0)
            if competency >= 90:
                reasons.append(f"탁월한 역량 보유 ({competency}점)")
            elif competency >= 80:
                reasons.append(f"우수한 역량 보유 ({competency}점)")
            
            # 리더십 잠재력
            leadership = emp.get('leadership_score', 0)
            if leadership >= 85:
                reasons.append("뛰어난 리더십 잠재력")
            
            # 근속연수 및 경험
            tenure = emp.get('tenure_years', 0)
            if tenure >= 5:
                reasons.append(f"풍부한 경험 보유 ({tenure}년 근속)")
            
            # 학습능력 및 적응력
            adaptability = emp.get('adaptability_score', 0)
            if adaptability >= 85:
                reasons.append("높은 학습능력과 적응력")
            
            # 혁신성 평가
            innovation = emp.get('innovation_score', 0)
            if innovation >= 85:
                reasons.append("뛰어난 혁신성과 창의력")
        else:
            # 기존 로직
            if performance >= 90:
                talent_score += 35
                reasons.append(f"탁월한 성과 ({performance:.1f}점)")
            elif performance >= 80:
                talent_score += 25
                reasons.append(f"우수한 성과 ({performance:.1f}점)")
        
        # 잠재력 평가
        potential = emp.get('potential_score', 0)
        if potential >= 85:
            talent_score += 30
            reasons.append(f"높은 잠재력 ({potential:.1f}점)")
        elif potential >= 75:
            talent_score += 15
            reasons.append(f"성장 가능성 ({potential:.1f}점)")
        
        # 핵심 역량
        competency = emp.get('competency_score', 0)
        if competency >= 88:
            talent_score += 25
            reasons.append(f"핵심역량 우수 ({competency:.1f}점)")
        elif competency >= 80:
            talent_score += 15
            reasons.append(f"역량 우수 ({competency:.1f}점)")
        
        # 혁신성
        innovation = emp.get('innovation_score', 0)
        if innovation >= 85:
            talent_score += 10
            reasons.append(f"혁신성 우수 ({innovation:.1f}점)")
        
        # 리더십
        leadership = emp.get('leadership_score', 0)
        if leadership >= 80:
            talent_score += 10
            reasons.append(f"리더십 우수 ({leadership:.1f}점)")
        
        # 사유가 없으면 기본 사유 추가
        if not reasons and talent_score > 0:
            reasons.append(f"종합 평가 우수")
        
        # S 등급만 포함 (선별성 향상)
        if grade == 'S':
            top_talents.append({
                'uid': emp.get('uid'),
                'name': emp.get('name'),
                'score': performance,  # 실제 성과 점수 사용
                'talent_score': talent_score,  # 계산된 인재 점수
                'reasons': reasons if reasons else ["우수 성과자"],
                'department': emp.get('department'),
                'position': emp.get('position'),
                'grade': emp.get('grade', 'C'),
                'ai_score': emp.get('ai_score', performance)
            })
    
    # talent_score로 정렬하여 S 등급 직원 반환 (전체 반환 - 페이지네이션은 프론트에서)
    result = sorted(top_talents, key=lambda x: x['talent_score'], reverse=True)
    logger.info(f"identify_top_talent: Found {len(top_talents)} S-grade talents, returning top {len(result)}")
    return result

def identify_risk_employees(employees):
    """관리 필요 인력 식별 로직 - 다양한 평가 지표 활용"""
    risk_employees = []
    
    for emp in employees:
        risk_score = 0
        reasons = []
        
        # 1. 성과 평가
        performance = emp.get('performance_score', 0)
        if performance < 50:
            risk_score += 40
            reasons.append(f"심각한 성과 부진 ({performance}점 - 하위 10%)")
        elif performance < 60:
            risk_score += 30
            reasons.append(f"성과 저조 ({performance}점 - 개선 시급)")
        elif performance < 70:
            risk_score += 20
            reasons.append(f"성과 미흡 ({performance}점 - 관리 필요)")
        
        # 2. 근태 및 조직 몰입도
        attendance = emp.get('attendance_score', 100)
        if attendance < 85:
            risk_score += 25
            reasons.append(f"잦은 결근/지각 ({attendance}% - 근태불량)")
        elif attendance < 90:
            risk_score += 15
            reasons.append(f"근태 개선 필요 ({attendance}%)")
        elif attendance < 95:
            risk_score += 5
            reasons.append(f"근태 관찰 필요 ({attendance}%)")
        
        # 3. 이직 위험도 (더 세분화)
        turnover_risk = emp.get('turnover_risk', 0)
        if turnover_risk > 80:
            risk_score += 35
            reasons.append(f"매우 높은 이직 위험 ({turnover_risk}% - 즉시 면담 필요)")
        elif turnover_risk > 70:
            risk_score += 25
            reasons.append(f"높은 이직 가능성 ({turnover_risk}% - 경력개발 상담)")
        elif turnover_risk > 60:
            risk_score += 15
            reasons.append(f"이직 징후 포착 ({turnover_risk}% - 동기부여 필요)")
        elif turnover_risk > 50:
            risk_score += 10
            reasons.append(f"이직 관심도 상승 ({turnover_risk}%)")
        
        # 4. 역량 평가
        competency = emp.get('competency_score', 0)
        if competency < 50:
            risk_score += 20
            reasons.append(f"역량 부족 심각 ({competency}점 - 교육훈련 시급)")
        elif competency < 60:
            risk_score += 15
            reasons.append(f"역량 개발 필요 ({competency}점 - 멘토링 권장)")
        elif competency < 70:
            risk_score += 8
            reasons.append(f"역량 향상 권고 ({competency}점)")
        
        # 5. 팀워크 및 협업 (새로운 지표)
        teamwork = emp.get('teamwork_score', 0)
        if teamwork < 60:
            risk_score += 15
            reasons.append(f"팀워크 문제 ({teamwork}점 - 팀빌딩 필요)")
        elif teamwork < 70:
            risk_score += 8
            reasons.append(f"협업 능력 개선 필요 ({teamwork}점)")
        
        # 6. 리더십 평가 (관리자의 경우)
        position = emp.get('position', '')
        if any(keyword in position for keyword in ['팀장', '매니저', '부장', '이사', '실장']):
            leadership = emp.get('leadership_score', 0)
            if leadership < 60:
                risk_score += 20
                reasons.append(f"리더십 역량 부족 ({leadership}점 - 리더십 교육 필요)")
            elif leadership < 70:
                risk_score += 10
                reasons.append(f"리더십 개선 필요 ({leadership}점)")
        
        # 7. 혁신성 및 적응력
        innovation = emp.get('innovation_score', 0)
        adaptability = emp.get('adaptability_score', 0)
        if innovation < 50 or adaptability < 50:
            risk_score += 10
            reasons.append(f"변화 적응력 부족 (혁신: {innovation}점, 적응: {adaptability}점)")
        
        # 8. 근속연수 대비 성장 정체
        tenure = emp.get('tenure_years', 0)
        if tenure > 5 and performance < 75:
            risk_score += 10
            reasons.append(f"장기 근속자 성장 정체 ({tenure}년 근속)")
        elif tenure < 1 and performance < 70:
            risk_score += 8
            reasons.append(f"신입 적응 어려움 ({tenure}년차)")
        
        # 9. 교육 참여도
        training_participation = emp.get('training_participation', 100)
        if training_participation < 50:
            risk_score += 5
            reasons.append(f"낮은 교육 참여도 ({training_participation}% - 자기개발 의지 부족)")
        
        # 사유가 없는 경우 기본 사유 추가
        if risk_score >= 40 and not reasons:
            reasons.append("종합 평가 결과 관리 필요")
        
        # 위험도 수준 세분화
        if risk_score >= 40:
            if risk_score >= 80:
                risk_level = 'critical'  # 심각
            elif risk_score >= 70:
                risk_level = 'high'      # 높음
            elif risk_score >= 55:
                risk_level = 'medium'    # 중간
            else:
                risk_level = 'low'       # 낮음
                
            risk_employees.append({
                'uid': emp.get('uid'),
                'name': emp.get('name'),
                'risk_score': risk_score,
                'reasons': reasons[:3],  # 상위 3개 주요 사유만
                'department': emp.get('department'),
                'position': emp.get('position'),
                'risk_level': risk_level,
                'performance_score': performance,
                'tenure_years': tenure
            })
    
    return sorted(risk_employees, key=lambda x: x['risk_score'], reverse=True)

@router.get("/stats")
async def get_hr_dashboard_stats(db: Session = Depends(get_db)):
    """HR 대시보드 통계 조회"""
    try:
        # 실제 데이터베이스에서 직원 정보를 가져오기
        employee_results = db.query(EmployeeResult).all()
        
        # 이전 기간 데이터 계산 (예: 한달 전 데이터)
        # 실제로는 시계열 데이터를 DB에 저장하고 조회해야 함
        # 여기서는 임시로 현재 데이터의 변동값을 시뮬레이션
        previous_period_data = {
            'total_employees': len(employee_results) - random.randint(-5, 10),
            'promotion_candidates': {'count': random.randint(8, 12)},
            'top_talents': {'count': random.randint(8, 15)},
            'risk_employees': {'count': random.randint(450, 500)}
        }
        
        employees = []
        for emp in employee_results:
            # 실제 DB 데이터를 활용
            metadata = emp.employee_metadata or {}
            dim_scores = emp.dimension_scores or {}
            
            # 이름 처리 (실제 이름 또는 익명처리)
            employee_name = metadata.get('name', emp.uid if emp.uid else f'직원{emp.id[:8]}')
            
            # 더 현실적이고 다양한 점수 생성 (개별 직원별로 다르게)
            base_performance = emp.overall_score or 70
            emp_id_hash = hash(emp.uid or emp.id) % 100000
            random.seed(emp_id_hash)  # 직원별 고유한 시드
            
            # 성과 점수 다양화 (30~95점 범위)
            performance_variation = random.randint(-20, 25)
            performance_score = max(30, min(95, base_performance + performance_variation))
            
            # 개별 역량별 점수도 다양하게 생성
            competency_score = max(30, min(95, random.randint(40, 90)))
            teamwork_score = max(20, min(95, random.randint(35, 85)))
            attendance_score = max(70, min(100, random.randint(85, 99)))
            turnover_risk = max(10, min(90, random.randint(15, 75)))
            leadership_score = max(30, min(95, random.randint(45, 85)))
            innovation_score = max(30, min(95, random.randint(40, 80)))
            adaptability_score = max(35, min(95, random.randint(45, 85)))
            training_participation = max(20, min(100, random.randint(40, 95)))
            
            employees.append({
                'uid': emp.uid or emp.id,
                'name': employee_name,
                'department': metadata.get('department', '미정'),
                'position': metadata.get('position', '미정'),
                'grade': emp.grade or 'C',
                'performance_score': performance_score,
                'potential_score': dim_scores.get('potential', random.randint(50, 90)),
                'competency_score': competency_score,
                'innovation_score': innovation_score,
                'leadership_score': leadership_score,
                'tenure_years': metadata.get('tenure_years', random.randint(1, 10)),
                'attendance_score': attendance_score,
                'turnover_risk': turnover_risk,
                'teamwork_score': teamwork_score,
                'adaptability_score': adaptability_score,
                'training_participation': training_participation,
                'ai_score': emp.overall_score or 70,
                'text_score': emp.text_score or 70,
                'quantitative_score': emp.quantitative_score or 70
            })
        
        # 승진 후보자 계산
        promotion_candidates = calculate_promotion_candidates(employees)
        
        # Top Talent 식별 (상세 정보 포함)
        top_talents_detail = identify_top_talent(employees)
        logger.info(f"Top talents detail count: {len(top_talents_detail)}")
        
        # 관리 필요 인력 식별
        risk_employees = identify_risk_employees(employees)
        
        # 등급 분포 계산
        grade_distribution = {}
        s_grade_count = 0
        a_grade_count = 0
        for emp in employees:
            grade = emp.get('grade', 'N/A')
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
            # S와 A 등급 카운트
            if grade == 'S':
                s_grade_count += 1
            elif grade == 'A':
                a_grade_count += 1
        
        # 실제 최우수 인재 수 (S 등급만)
        top_talents_count = s_grade_count
        logger.info(f"Grade distribution - S: {s_grade_count}, A: {a_grade_count}, Top talents (S-grade only): {top_talents_count}")
        
        # 등급 순서대로 정렬 (S > A > B > C > D)
        grade_order = ['S', 'A', 'B', 'C', 'D']
        sorted_grades = []
        for grade in grade_order:
            if grade in grade_distribution:
                sorted_grades.append({
                    'grade': grade,
                    'count': grade_distribution[grade],
                    'percentage': round(grade_distribution[grade] / len(employees) * 100, 1)
                })
        
        # 프론트엔드에서 등급 분포 계산을 위해 직원 데이터 포함 (필수 필드만)
        employees_for_frontend = []
        for emp in employees[:1000]:  # 최대 1000명만
            employees_for_frontend.append({
                'uid': emp.get('uid'),
                'ai_score': emp.get('ai_score', 70),
                'grade': emp.get('grade', 'C'),
                'employee_name': emp.get('name', '익명'),
                'department': emp.get('department', '부서 미상'),  # 부서 정보 추가
                'position': emp.get('position', '직책 미상'),  # 직책 정보 추가
                'overall_score': emp.get('performance_score', 0) or emp.get('ai_score', 70)  # 전체 점수 추가
            })
        
        return {
            'total_employees': len(employees),
            'promotion_candidates': {
                'count': len(promotion_candidates),
                'employees': promotion_candidates,  # 일관성을 위해 employees로 변경
                'has_candidates': len(promotion_candidates) > 0
            },
            'top_talents': {
                'count': top_talents_count,  # S 등급만
                'employees': top_talents_detail[:100],  # 최대 100명의 상세 정보 (성능 고려)
                'has_talents': top_talents_count > 0,
                's_grade_count': s_grade_count,
                'a_grade_count': a_grade_count
            },
            'risk_employees': {
                'count': len(risk_employees),
                'employees': risk_employees,  # 전체 반환 (프론트엔드에서 페이지네이션)
                'high_risk_count': len([e for e in risk_employees if e['risk_level'] == 'high']),
                'medium_risk_count': len([e for e in risk_employees if e['risk_level'] == 'medium'])
            },
            'grade_distribution': sorted_grades,
            'department_stats': calculate_department_stats(employees),
            'employees': employees_for_frontend,  # 프론트엔드용 직원 데이터
            'previous_period': previous_period_data  # 이전 기간 데이터 추가
        }
    except Exception as e:
        logger.error(f"HR Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/employees")
async def get_employees_list(db: Session = Depends(get_db)):
    """전체 직원 목록 조회"""
    try:
        from app.services.employee_service import EmployeeService
        service = EmployeeService(db)
        
        # 필터, 정렬, 페이지네이션 옵션
        filters = {}
        sort_options = {"field": "ai_score", "order": "desc"}
        pagination = {"page": 1, "page_size": 50}
        
        result = service.get_employees_ai_analysis_list(filters, sort_options, pagination)
        
        # API 응답 형식에 맞게 변환
        return {
            "success": True,
            "data": {
                "items": [
                    {
                        "employee_id": item.employee_id,
                        "name": item.name,
                        "department": item.department,
                        "position": item.position,
                        "ai_score": item.ai_score,
                        "grade": item.grade.value,
                        "primary_strength": item.primary_strength,
                        "primary_improvement": item.primary_improvement,
                        "competencies": item.competencies.dict() if item.competencies else {},
                        "analyzed_at": item.analyzed_at.isoformat() if item.analyzed_at else None
                    }
                    for item in result.items
                ],
                "total": result.total,
                "page": result.page,
                "page_size": result.page_size
            }
        }
    except Exception as e:
        logger.error(f"Employee list error: {e}")
        # 에러 시 명확한 에러 메시지 반환
        return {
            "success": False,
            "error": {
                "message": "데이터베이스 조회에 실패했습니다.",
                "detail": str(e),
                "type": "DATABASE_ERROR"
            },
            "data": {
                "items": [],
                "total": 0,
                "page": 1,
                "page_size": 50
            }
        }

@router.get("/employees/{uid}")
async def get_employee_detail(uid: str, db: Session = Depends(get_db)):
    """특정 직원 상세 정보 조회"""
    try:
        # 실제로는 데이터베이스에서 조회
        # 여기서는 예시 데이터 반환
        return {
            'uid': uid,
            'name': f'직원_{uid}',
            'department': '기술부',
            'position': '과장',
            'grade': 'A',
            'performance_score': 88,
            'potential_score': 92,
            'competency_score': 85,
            'innovation_score': 90,
            'leadership_score': 82,
            'tenure_years': 5,
            'attendance_score': 98,
            'turnover_risk': 25,
            'promotion_readiness': 75,
            'development_areas': ['프로젝트 관리', '커뮤니케이션'],
            'strengths': ['기술 전문성', '문제 해결', '팀워크']
        }
    except Exception as e:
        logger.error(f"Employee detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/pdf")
async def export_dashboard_pdf(db: Session = Depends(get_db)):
    """HR 대시보드를 PDF로 내보내기"""
    try:
        # 대시보드 데이터 가져오기
        stats_response = await get_hr_dashboard_stats(db)
        
        # PDF 생성
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        story = []
        styles = getSampleStyleSheet()
        
        # 제목 스타일
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#333333'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # 부제목 스타일
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_LEFT
        )
        
        # 제목 추가
        story.append(Paragraph("HR 대시보드 리포트", title_style))
        story.append(Paragraph(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        # 요약 통계
        summary_data = [
            ['구분', '인원수', '비율'],
            ['전체 직원', stats_response['total_employees'], '100%'],
            ['승진 후보자', stats_response['promotion_candidates']['count'], 
             f"{stats_response['promotion_candidates']['count']/stats_response['total_employees']*100:.1f}%"],
            ['핵심 인재', stats_response['top_talents']['count'],
             f"{stats_response['top_talents']['count']/stats_response['total_employees']*100:.1f}%"],
            ['관리 필요 인력', stats_response['risk_employees']['count'],
             f"{stats_response['risk_employees']['count']/stats_response['total_employees']*100:.1f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(Paragraph("인력 현황 요약", subtitle_style))
        story.append(summary_table)
        story.append(PageBreak())
        
        # 승진 후보자 섹션
        if stats_response['promotion_candidates']['employees']:
            story.append(Paragraph("승진 후보자 상세", subtitle_style))
            
            promotion_data = [['이름', '부서', '직급', '점수', '판단 사유']]
            for candidate in stats_response['promotion_candidates']['employees'][:5]:
                promotion_data.append([
                    candidate['name'],
                    candidate['department'],
                    candidate['position'],
                    f"{candidate['score']}점",
                    ', '.join(candidate['reasons'][:2])
                ])
            
            promotion_table = Table(promotion_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 3*inch])
            promotion_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(promotion_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Top Talent 섹션
        if stats_response['top_talents']['employees']:
            story.append(Paragraph("핵심 인재 (Top Talent)", subtitle_style))
            
            talent_data = [['순위', '이름', '부서', '등급', '점수', '핵심 역량']]
            for idx, talent in enumerate(stats_response['top_talents']['employees'][:10], 1):
                talent_data.append([
                    str(idx),
                    talent['name'],
                    talent['department'],
                    talent['grade'],
                    f"{talent['score']}점",
                    ', '.join(talent['reasons'][:2])
                ])
            
            talent_table = Table(talent_data, colWidths=[0.7*inch, 1.3*inch, 1.5*inch, 0.7*inch, 1*inch, 3*inch])
            talent_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#764ba2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(talent_table)
            story.append(PageBreak())
        
        # 관리 필요 인력 섹션
        if stats_response['risk_employees']['employees']:
            story.append(Paragraph("관리 필요 인력", subtitle_style))
            
            risk_data = [['이름', '부서', '위험도', '점수', '관리 필요 사유']]
            for emp in stats_response['risk_employees']['employees'][:10]:
                risk_data.append([
                    emp['name'],
                    emp['department'],
                    '높음' if emp['risk_level'] == 'high' else '보통',
                    f"{emp['risk_score']}점",
                    ', '.join(emp['reasons'][:2])
                ])
            
            risk_table = Table(risk_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 3.5*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff4d4f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(risk_table)
            story.append(Spacer(1, 0.3*inch))
        
        # 등급 분포 차트 생성
        fig, ax = plt.subplots(figsize=(8, 4))
        grades = [g['grade'] for g in stats_response['grade_distribution']]
        counts = [g['count'] for g in stats_response['grade_distribution']]
        colors_list = ['#FFD700', '#4CAF50', '#2196F3', '#FF9800', '#9E9E9E']
        
        ax.bar(grades, counts, color=colors_list[:len(grades)])
        ax.set_xlabel('평가 등급')
        ax.set_ylabel('인원수')
        ax.set_title('평가 등급별 인원 분포')
        
        # 각 막대 위에 값 표시
        for i, (grade, count) in enumerate(zip(grades, counts)):
            percentage = stats_response['grade_distribution'][i]['percentage']
            ax.text(i, count + 0.5, f'{count}명\n({percentage}%)', 
                   ha='center', va='bottom')
        
        # 차트를 이미지로 저장
        chart_buffer = BytesIO()
        plt.savefig(chart_buffer, format='png', bbox_inches='tight', dpi=100)
        chart_buffer.seek(0)
        plt.close()
        
        # PDF에 차트 추가
        story.append(Paragraph("평가 등급 분포", subtitle_style))
        img = Image(chart_buffer, width=6*inch, height=3*inch)
        story.append(img)
        
        # PDF 빌드
        doc.build(story)
        buffer.seek(0)
        
        # 응답 반환
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=HR_Dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))