"""
HR Dashboard API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.db import get_db
import logging
import random

logger = logging.getLogger(__name__)
router = APIRouter()

def calculate_promotion_candidates(employees):
    """승진 후보자 예측 로직"""
    candidates = []
    
    for emp in employees:
        promotion_score = 0
        reasons = []
        
        # 평가 등급이 우수한 경우
        if emp.get('grade', '') in ['S', 'A']:
            promotion_score += 40
            reasons.append(f"우수 평가등급 ({emp.get('grade')})")
        
        # 근속연수가 3년 이상인 경우
        tenure = emp.get('tenure_years', 0)
        if tenure >= 3:
            promotion_score += 20
            reasons.append(f"충분한 근속연수 ({tenure}년)")
        
        # 역량점수가 높은 경우
        competency = emp.get('competency_score', 0)
        if competency >= 85:
            promotion_score += 30
            reasons.append(f"높은 역량점수 ({competency}점)")
        
        # 리더십 점수가 높은 경우
        leadership = emp.get('leadership_score', 0)
        if leadership >= 80:
            promotion_score += 10
            reasons.append(f"우수한 리더십 ({leadership}점)")
        
        if promotion_score >= 70:
            candidates.append({
                'uid': emp.get('uid'),
                'name': emp.get('name'),
                'score': promotion_score,
                'reasons': reasons,
                'department': emp.get('department'),
                'position': emp.get('position')
            })
    
    return sorted(candidates, key=lambda x: x['score'], reverse=True)

def identify_top_talent(employees):
    """Top Talent 식별 로직"""
    top_talents = []
    
    for emp in employees:
        talent_score = 0
        reasons = []
        
        # 종합 성과 점수
        performance = emp.get('performance_score', 0)
        if performance >= 90:
            talent_score += 35
            reasons.append(f"탁월한 성과 ({performance}점)")
        elif performance >= 80:
            talent_score += 25
            reasons.append(f"우수한 성과 ({performance}점)")
        
        # 잠재력 평가
        potential = emp.get('potential_score', 0)
        if potential >= 85:
            talent_score += 30
            reasons.append(f"높은 잠재력 ({potential}점)")
        
        # 핵심 역량
        competency = emp.get('competency_score', 0)
        if competency >= 88:
            talent_score += 25
            reasons.append(f"핵심역량 우수 ({competency}점)")
        
        # 혁신성
        innovation = emp.get('innovation_score', 0)
        if innovation >= 85:
            talent_score += 10
            reasons.append(f"혁신성 우수 ({innovation}점)")
        
        if talent_score >= 65:
            top_talents.append({
                'uid': emp.get('uid'),
                'name': emp.get('name'),
                'score': talent_score,
                'reasons': reasons,
                'department': emp.get('department'),
                'position': emp.get('position'),
                'grade': emp.get('grade')
            })
    
    return sorted(top_talents, key=lambda x: x['score'], reverse=True)[:10]

def identify_risk_employees(employees):
    """관리 필요 인력 식별 로직"""
    risk_employees = []
    
    for emp in employees:
        risk_score = 0
        reasons = []
        
        # 성과 부진
        performance = emp.get('performance_score', 0)
        if performance < 60:
            risk_score += 40
            reasons.append(f"성과 부진 ({performance}점)")
        elif performance < 70:
            risk_score += 25
            reasons.append(f"성과 개선 필요 ({performance}점)")
        
        # 근태 문제
        attendance = emp.get('attendance_score', 100)
        if attendance < 90:
            risk_score += 20
            reasons.append(f"근태 관리 필요 ({attendance}%)")
        
        # 이직 위험도
        turnover_risk = emp.get('turnover_risk', 0)
        if turnover_risk > 70:
            risk_score += 30
            reasons.append(f"높은 이직 위험도 ({turnover_risk}%)")
        elif turnover_risk > 50:
            risk_score += 15
            reasons.append(f"이직 위험 관찰 필요 ({turnover_risk}%)")
        
        # 역량 부족
        competency = emp.get('competency_score', 0)
        if competency < 60:
            risk_score += 10
            reasons.append(f"역량 개발 필요 ({competency}점)")
        
        if risk_score >= 40:
            risk_employees.append({
                'uid': emp.get('uid'),
                'name': emp.get('name'),
                'risk_score': risk_score,
                'reasons': reasons,
                'department': emp.get('department'),
                'position': emp.get('position'),
                'risk_level': 'high' if risk_score >= 70 else 'medium'
            })
    
    return sorted(risk_employees, key=lambda x: x['risk_score'], reverse=True)

@router.get("/stats")
async def get_hr_dashboard_stats(db: Session = Depends(get_db)):
    """HR 대시보드 통계 조회"""
    try:
        # 실제 데이터베이스에서 직원 정보를 가져오는 로직
        # 여기서는 예시 데이터 생성
        employees = []
        for i in range(100):
            employees.append({
                'uid': f'EMP{i:04d}',
                'name': f'직원{i}',
                'department': ['영업부', '기술부', '인사부', '재무부', '마케팅부'][i % 5],
                'position': ['사원', '대리', '과장', '차장', '부장'][i % 5],
                'grade': ['S', 'A', 'B', 'C', 'D'][min(i % 6, 4)],
                'performance_score': random.randint(50, 100),
                'potential_score': random.randint(60, 100),
                'competency_score': random.randint(55, 100),
                'innovation_score': random.randint(50, 95),
                'leadership_score': random.randint(40, 95),
                'tenure_years': random.randint(1, 15),
                'attendance_score': random.randint(85, 100),
                'turnover_risk': random.randint(10, 80)
            })
        
        # 승진 후보자 계산
        promotion_candidates = calculate_promotion_candidates(employees)
        
        # Top Talent 식별
        top_talents = identify_top_talent(employees)
        
        # 관리 필요 인력 식별
        risk_employees = identify_risk_employees(employees)
        
        # 등급 분포 계산
        grade_distribution = {}
        for emp in employees:
            grade = emp.get('grade', 'N/A')
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
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
        
        return {
            'total_employees': len(employees),
            'promotion_candidates': {
                'count': len(promotion_candidates),
                'candidates': promotion_candidates[:5],  # 상위 5명만 표시
                'has_candidates': len(promotion_candidates) > 0
            },
            'top_talents': {
                'count': len(top_talents),
                'employees': top_talents,
                'has_talents': len(top_talents) > 0
            },
            'risk_employees': {
                'count': len(risk_employees),
                'employees': risk_employees[:10],  # 상위 10명만 표시
                'high_risk_count': len([e for e in risk_employees if e['risk_level'] == 'high']),
                'medium_risk_count': len([e for e in risk_employees if e['risk_level'] == 'medium'])
            },
            'grade_distribution': sorted_grades,
            'department_stats': {
                '영업부': {'count': 20, 'avg_score': 78.5},
                '기술부': {'count': 20, 'avg_score': 82.3},
                '인사부': {'count': 20, 'avg_score': 76.8},
                '재무부': {'count': 20, 'avg_score': 79.2},
                '마케팅부': {'count': 20, 'avg_score': 77.4}
            }
        }
    except Exception as e:
        logger.error(f"HR Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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