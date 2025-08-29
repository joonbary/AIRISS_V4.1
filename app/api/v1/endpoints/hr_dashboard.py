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
    """승진 후보자 예측 로직"""
    candidates = []
    logger.info(f"calculate_promotion_candidates: Processing {len(employees)} employees")
    
    # 디버깅을 위해 처음 3명의 데이터 확인
    for idx, emp in enumerate(employees[:3]):
        logger.info(f"Employee {idx}: grade={emp.get('grade')}, tenure={emp.get('tenure_years')}, competency={emp.get('competency_score')}, performance={emp.get('performance_score')}, leadership={emp.get('leadership_score')}")
    
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
        
        # 승진 후보자 기준 완화 (최소 50점)
        if promotion_score >= 50:
            candidates.append({
                'uid': emp.get('uid'),
                'name': emp.get('name'),
                'score': promotion_score,
                'reasons': reasons,
                'department': emp.get('department'),
                'position': emp.get('position'),
                'grade': emp.get('grade', 'C')
            })
    
    # 점수순 정렬하고 최대 10명으로 제한
    result = sorted(candidates, key=lambda x: x['score'], reverse=True)[:10]
    
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
        
        # S 등급만 핵심인재로 제한하여 선별성 높이기
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
    
    # talent_score로 정렬하여 S 등급 직원 반환 (최대 10명으로 제한)
    result = sorted(top_talents, key=lambda x: x['talent_score'], reverse=True)[:10]
    logger.info(f"identify_top_talent: Found {len(top_talents)} S-grade talents, returning top {len(result)}")
    return result

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
        # 실제 데이터베이스에서 직원 정보를 가져오기
        employee_results = db.query(EmployeeResult).all()
        
        employees = []
        for emp in employee_results:
            # 실제 DB 데이터를 활용
            metadata = emp.employee_metadata or {}
            dim_scores = emp.dimension_scores or {}
            
            # 이름 처리 (실제 이름 또는 익명처리)
            employee_name = metadata.get('name', emp.uid if emp.uid else f'직원{emp.id[:8]}')
            
            employees.append({
                'uid': emp.uid or emp.id,
                'name': employee_name,
                'department': metadata.get('department', '미정'),
                'position': metadata.get('position', '미정'),
                'grade': emp.grade or 'C',
                'performance_score': emp.overall_score or 70,
                'potential_score': dim_scores.get('potential', 70),
                'competency_score': dim_scores.get('competency', 70),
                'innovation_score': dim_scores.get('innovation', 70),
                'leadership_score': dim_scores.get('leadership', 60),
                'tenure_years': metadata.get('tenure_years', 1),
                'attendance_score': metadata.get('attendance', 95),
                'turnover_risk': metadata.get('turnover_risk', 30),
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
                'employees': risk_employees[:50],  # 최대 50명까지 반환 (페이지네이션용)
                'high_risk_count': len([e for e in risk_employees if e['risk_level'] == 'high']),
                'medium_risk_count': len([e for e in risk_employees if e['risk_level'] == 'medium'])
            },
            'grade_distribution': sorted_grades,
            'department_stats': calculate_department_stats(employees),
            'employees': employees_for_frontend  # 프론트엔드용 직원 데이터
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