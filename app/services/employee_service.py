"""
AIRISS v4.2 직원 AI 분석 서비스
Employee AI Analysis Service Layer
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
import json
import pandas as pd
from pathlib import Path

from app.models.file import File
from app.models.analysis_result import AnalysisResultModel as AnalysisResult, AnalysisJobModel
from app.models.employee import EmployeeResult
from app.schemas.employee import (
    EmployeeAIAnalysis,
    EmployeeAIAnalysisSummary,
    EmployeeAIAnalysisList,
    AIRecommendation,
    RecommendationType,
    CompetencyScores,
    AIGrade,
    CompetencyRadarData,
    DashboardStatistics
)

logger = logging.getLogger(__name__)


class EmployeeService:
    """직원 AI 분석 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def _map_grade(self, ok_grade: str) -> AIGrade:
        """OK등급을 AIGrade Enum으로 변환"""
        grade_mapping = {
            "S": AIGrade.S,
            "A+": AIGrade.A_PLUS,
            "A": AIGrade.A,
            "B": AIGrade.B,
            "C": AIGrade.C,
            "D": AIGrade.D
        }
        return grade_mapping.get(ok_grade, AIGrade.C)
    
    def _extract_competencies(self, analysis_data: Dict[str, Any]) -> CompetencyScores:
        """분석 데이터에서 8대 역량 점수 추출"""
        competency_mapping = {
            "실행력_정량점수": "실행력",
            "성장지향_정량점수": "성장지향",
            "협업_정량점수": "협업",
            "고객지향_정량점수": "고객지향",
            "전문성_정량점수": "전문성",
            "혁신성_정량점수": "혁신성",
            "리더십_정량점수": "리더십",
            "커뮤니케이션_정량점수": "커뮤니케이션"
        }
        
        scores = {}
        for key, field in competency_mapping.items():
            score = analysis_data.get(key, 50)  # 기본값 50
            scores[field] = int(score) if score else 50
            
        return CompetencyScores(**scores)
    
    def _extract_strengths_improvements(self, analysis_data: Dict[str, Any]) -> tuple:
        """강점과 개선점 추출"""
        # AI_장점에서 상위 3개 추출
        strengths_text = analysis_data.get("AI_장점", "")
        strengths = []
        if strengths_text:
            # 간단한 파싱 로직 - 실제로는 더 정교한 NLP 필요
            strengths = [s.strip() for s in strengths_text.split(",")][:3]
        
        # AI_개선점에서 상위 2개 추출
        improvements_text = analysis_data.get("AI_개선점", "")
        improvements = []
        if improvements_text:
            improvements = [i.strip() for i in improvements_text.split(",")][:2]
            
        return strengths, improvements
    
    def get_employee_ai_analysis(self, employee_id: str) -> Optional[EmployeeAIAnalysis]:
        """특정 직원의 AI 분석 결과 조회 - 기존 analysis_results에서 풍부한 데이터 가져오기"""
        try:
            logger.info(f"🔍 직원 AI 분석 조회 시작 - ID: {employee_id}")
            
            # 1차: 기존 analysis_results 테이블에서 풍부한 AI 분석 데이터 조회
            analysis_result = self.db.query(AnalysisResult).filter(
                AnalysisResult.uid == employee_id
            ).order_by(AnalysisResult.created_at.desc()).first()
            
            if analysis_result:
                logger.info(f"✅ 기존 분석결과 발견 - 풍부한 AI 피드백 데이터 사용")
                
                # AI 피드백에서 상세 정보 추출
                ai_feedback = analysis_result.ai_feedback or {}
                ai_strengths = analysis_result.ai_strengths or ""
                ai_weaknesses = analysis_result.ai_weaknesses or ""
                ai_recommendations = analysis_result.ai_recommendations or {}
                
                # 강점을 리스트로 파싱 (기존 AI 피드백 형식)
                strengths = []
                if ai_strengths:
                    # "[장점]" 섹션에서 항목들 추출
                    strength_lines = ai_strengths.split('\n')
                    for line in strength_lines:
                        if line.strip() and not line.startswith('[') and not line.startswith('장점'):
                            # 번호와 기호 제거 후 추가
                            clean_line = line.strip().lstrip('123456789.-• ').strip()
                            if clean_line:
                                strengths.append(clean_line)
                
                # 개선점을 리스트로 파싱
                improvements = []
                if ai_weaknesses:
                    weakness_lines = ai_weaknesses.split('\n')
                    for line in weakness_lines:
                        if line.strip() and not line.startswith('[') and not line.startswith('개선'):
                            clean_line = line.strip().lstrip('123456789.-• ').strip()
                            if clean_line:
                                improvements.append(clean_line)
                
                # 8대 역량 점수 추출 (기존 데이터 구조 활용)
                dimension_scores = analysis_result.dimension_scores or {}
                competencies = CompetencyScores(
                    실행력=int(dimension_scores.get("실행력_정량점수", dimension_scores.get("problem_solving", 75))),
                    성장지향=int(dimension_scores.get("성장지향_정량점수", dimension_scores.get("adaptability", 75))),
                    협업=int(dimension_scores.get("협업_정량점수", dimension_scores.get("teamwork", 70))),
                    고객지향=int(dimension_scores.get("고객지향_정량점수", dimension_scores.get("customer_focus", 80))),
                    전문성=int(dimension_scores.get("전문성_정량점수", dimension_scores.get("technical", 75))),
                    혁신성=int(dimension_scores.get("혁신성_정량점수", dimension_scores.get("innovation", 70))),
                    리더십=int(dimension_scores.get("리더십_정량점수", dimension_scores.get("leadership", 65))),
                    커뮤니케이션=int(dimension_scores.get("커뮤니케이션_정량점수", dimension_scores.get("communication", 75)))
                )
                
                # AI 추천사항 파싱
                career_recommendations = []
                education_suggestions = []
                
                if isinstance(ai_recommendations, dict):
                    career_recommendations = ai_recommendations.get("career", ["프로젝트 관리 역량 강화", "팀 리더십 개발"])
                    education_suggestions = ai_recommendations.get("education", ["리더십 교육 프로그램", "전략적 사고 워크샵"])
                
                # AI 종합 피드백 (기존 시스템의 풍부한 피드백)
                ai_comment = ai_feedback.get("ai_feedback", ai_feedback.get("overall_comment", ""))
                if not ai_comment and ai_strengths and ai_weaknesses:
                    ai_comment = f"주요 강점: {ai_strengths[:200]}... 개선 필요 영역: {ai_weaknesses[:200]}..."
                
                # 파일에서 직원 정보 추출
                from app.models.file import File
                file_info = self.db.query(File).filter(File.id == analysis_result.file_id).first()
                name = "직원"  # 기본값
                department = "미지정"
                position = "미지정"
                
                result = EmployeeAIAnalysis(
                    employee_id=employee_id,
                    name=name,
                    department=department,
                    position=position,
                    profile_image=None,
                    ai_score=int(analysis_result.hybrid_score) if analysis_result.hybrid_score else 0,
                    grade=self._map_grade(analysis_result.ok_grade),
                    competencies=competencies,
                    strengths=strengths[:5],  # 상위 5개 강점
                    improvements=improvements[:3],  # 상위 3개 개선점
                    ai_comment=ai_comment,
                    career_recommendation=career_recommendations,
                    education_suggestion=education_suggestions,
                    analyzed_at=analysis_result.created_at,
                    model_version="AIRISS v4.2"
                )
                
                logger.info(f"📤 풍부한 AI 분석 데이터 반환 - 강점: {len(strengths)}, 개선점: {len(improvements)}")
                return result
            
            # 2차: employee_results 테이블 조회 (fallback)
            employee_results = self.db.query(EmployeeResult).filter(
                EmployeeResult.uid == employee_id
            ).all()
            
            if not employee_results:
                logger.warning(f"❌ 직원 {employee_id}의 데이터를 찾을 수 없음")
                return None
            
            # 메타데이터가 있는 것을 우선적으로 선택
            employee_result = None
            for result in employee_results:
                if result.employee_metadata and result.employee_metadata.get('name'):
                    employee_result = result
                    break
            
            if not employee_result:
                employee_result = employee_results[0]
            
            # 기본 데이터로 반환 (기존 로직)
            metadata = employee_result.employee_metadata or {}
            name = metadata.get("name", "Unknown")
            department = metadata.get("department", "미지정")
            position = metadata.get("position", "미지정")
            
            competencies = CompetencyScores(
                실행력=75, 성장지향=75, 협업=70, 고객지향=80,
                전문성=75, 혁신성=70, 리더십=65, 커뮤니케이션=75
            )
            
            result = EmployeeAIAnalysis(
                employee_id=employee_id,
                name=name,
                department=department,
                position=position,
                profile_image=None,
                ai_score=int(employee_result.overall_score) if employee_result.overall_score else 0,
                grade=self._map_grade(employee_result.grade),
                competencies=competencies,
                strengths=["기본 업무 능력", "성실성"],
                improvements=["전문성 향상", "리더십 개발"],
                ai_comment="기본 분석 결과입니다.",
                career_recommendation=["프로젝트 관리", "팀 리더십"],
                education_suggestion=["리더십 교육", "전략적 사고 프로그램"],
                analyzed_at=datetime.now(),
                model_version="v4.2"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"직원 AI 분석 조회 실패: {e}")
            return None
    
    def get_employees_ai_analysis_list(
        self,
        filters: Dict[str, Any],
        sort_options: Dict[str, str],
        pagination: Dict[str, int]
    ) -> EmployeeAIAnalysisList:
        """전체 직원 AI 분석 목록 조회 - 기존 analysis_results 우선 활용"""
        try:
            # 1차: 기존 analysis_results 테이블에서 데이터 조회
            from sqlalchemy import func, and_
            
            # 각 uid별로 가장 최신 분석 결과만 선택
            subquery = self.db.query(
                AnalysisResult.uid,
                func.max(AnalysisResult.id).label('max_id')
            ).group_by(AnalysisResult.uid).subquery()
            
            analysis_query = self.db.query(AnalysisResult).join(
                subquery,
                and_(
                    AnalysisResult.uid == subquery.c.uid,
                    AnalysisResult.id == subquery.c.max_id
                )
            )
            
            # 정렬 옵션 적용
            sort_field = sort_options.get("field", "hybrid_score")
            sort_order = sort_options.get("order", "desc")
            
            if sort_field == "ai_score":
                sort_field = "hybrid_score"
            
            if hasattr(AnalysisResult, sort_field):
                if sort_order == "desc":
                    analysis_query = analysis_query.order_by(getattr(AnalysisResult, sort_field).desc())
                else:
                    analysis_query = analysis_query.order_by(getattr(AnalysisResult, sort_field).asc())
            
            # 페이징 적용
            page = pagination.get("page", 1)
            page_size = pagination.get("page_size", 20)
            offset = (page - 1) * page_size
            
            analysis_results = analysis_query.offset(offset).limit(page_size).all()
            total_from_analysis = analysis_query.count()
            
            # AnalysisResult 데이터를 EmployeeAIAnalysisSummary로 변환
            items = []
            for result in analysis_results:
                # AI 피드백에서 간단한 정보 추출
                ai_feedback = result.ai_feedback or {}
                dimension_scores = result.dimension_scores or {}
                
                # 주요 강점과 개선점 추출 (간단한 파싱)
                ai_strengths = result.ai_strengths or ""
                primary_strength = "우수한 업무 능력"
                if ai_strengths:
                    lines = [line.strip().lstrip('123456789.-• ').strip() 
                            for line in ai_strengths.split('\n') 
                            if line.strip() and not line.startswith('[')]
                    if lines:
                        primary_strength = lines[0][:50] + ("..." if len(lines[0]) > 50 else "")
                
                ai_weaknesses = result.ai_weaknesses or ""
                primary_improvement = "전문성 향상"
                if ai_weaknesses:
                    lines = [line.strip().lstrip('123456789.-• ').strip() 
                            for line in ai_weaknesses.split('\n') 
                            if line.strip() and not line.startswith('[')]
                    if lines:
                        primary_improvement = lines[0][:50] + ("..." if len(lines[0]) > 50 else "")
                
                competencies = CompetencyScores(
                    실행력=int(dimension_scores.get("실행력_정량점수", dimension_scores.get("problem_solving", 75))),
                    성장지향=int(dimension_scores.get("성장지향_정량점수", dimension_scores.get("adaptability", 75))),
                    협업=int(dimension_scores.get("협업_정량점수", dimension_scores.get("teamwork", 70))),
                    고객지향=int(dimension_scores.get("고객지향_정량점수", dimension_scores.get("customer_focus", 80))),
                    전문성=int(dimension_scores.get("전문성_정량점수", dimension_scores.get("technical", 75))),
                    혁신성=int(dimension_scores.get("혁신성_정량점수", dimension_scores.get("innovation", 70))),
                    리더십=int(dimension_scores.get("리더십_정량점수", dimension_scores.get("leadership", 65))),
                    커뮤니케이션=int(dimension_scores.get("커뮤니케이션_정량점수", dimension_scores.get("communication", 75)))
                )
                
                summary = EmployeeAIAnalysisSummary(
                    employee_id=result.uid,
                    name=f"직원_{result.uid[-4:]}",  # UID 마지막 4자리로 이름 생성
                    department="미지정",
                    position="미지정",
                    ai_score=int(result.hybrid_score) if result.hybrid_score else 0,
                    grade=self._map_grade(result.ok_grade),
                    primary_strength=primary_strength,
                    primary_improvement=primary_improvement,
                    competencies=competencies,
                    analyzed_at=result.created_at
                )
                items.append(summary)
            
            # 2차: employee_results 테이블에서 추가 데이터 조회 (analysis_results에 없는 경우)
            if len(items) < page_size:
                # analysis_results에서 이미 조회한 uid들 제외
                existing_uids = [item.employee_id for item in items]
                
                employee_subquery = self.db.query(
                    EmployeeResult.uid,
                    func.max(EmployeeResult.id).label('max_id')
                ).filter(~EmployeeResult.uid.in_(existing_uids)).group_by(EmployeeResult.uid).subquery()
                
                employee_query = self.db.query(EmployeeResult).join(
                    employee_subquery,
                    and_(
                        EmployeeResult.uid == employee_subquery.c.uid,
                        EmployeeResult.id == employee_subquery.c.max_id
                    )
                )
                
                remaining_limit = page_size - len(items)
                employee_results = employee_query.limit(remaining_limit).all()
                
                # EmployeeResult 데이터 변환
                for result in employee_results:
                    metadata = result.employee_metadata or {}
                    
                    competencies = CompetencyScores(
                        실행력=75, 성장지향=75, 협업=70, 고객지향=80,
                        전문성=75, 혁신성=70, 리더십=65, 커뮤니케이션=75
                    )
                    
                    summary = EmployeeAIAnalysisSummary(
                        employee_id=result.uid,
                        name=metadata.get("name", f"직원_{result.uid[-4:]}"),
                        department=metadata.get("department", "미지정"),
                        position=metadata.get("position", "미지정"),
                        ai_score=int(result.overall_score) if result.overall_score else 0,
                        grade=self._map_grade(result.grade),
                        primary_strength="기본 업무 능력",
                        primary_improvement="전문성 향상",
                        competencies=competencies,
                        analyzed_at=datetime.now()
                    )
                    items.append(summary)
            
            # 전체 개수는 두 테이블 합계
            employee_total = self.db.query(EmployeeResult.uid).distinct().count()
            total_count = max(total_from_analysis, employee_total)
            
            logger.info(f"📋 직원 목록 조회 완료 - 총 {len(items)}명, 전체 {total_count}명")
            
            return EmployeeAIAnalysisList(
                items=items,
                total=total_count,
                page=page,
                page_size=page_size,
                total_pages=(total_count + page_size - 1) // page_size
            )
            
        except Exception as e:
            logger.error(f"직원 AI 분석 목록 조회 실패: {e}")
            return EmployeeAIAnalysisList(items=[], total=0, page=1, page_size=20, total_pages=0)
            
            
    def _legacy_get_employees_list(self, filters, sort_options, pagination):
        """기존 employee_results 테이블 조회 (fallback)"""
        try:
            from sqlalchemy import func, and_
            
            # 각 uid별 최신 id를 구하는 서브쿼리  
            subquery = self.db.query(
                EmployeeResult.uid,
                func.max(EmployeeResult.id).label('max_id')
            ).group_by(EmployeeResult.uid).subquery()
            
            # 메인 쿼리
            query = self.db.query(EmployeeResult).join(
                subquery,
                and_(
                    EmployeeResult.uid == subquery.c.uid,
                    EmployeeResult.id == subquery.c.max_id
                )
            )
            
            # 필터 적용
            if filters.get("department"):
                query = query.filter(func.json_extract(EmployeeResult.employee_metadata, "$.department") == filters["department"])
            if filters.get("position"):
                query = query.filter(func.json_extract(EmployeeResult.employee_metadata, "$.position") == filters["position"])
            if filters.get("grade"):
                query = query.filter(EmployeeResult.grade == filters["grade"])
            if filters.get("search"):
                # 이름 또는 직원번호로 검색
                search_term = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        EmployeeResult.uid.like(search_term),
                        func.json_extract(EmployeeResult.employee_metadata, "$.name").like(search_term)
                    )
                )
            
            # 정렬 적용
            sort_field = sort_options.get("field", "overall_score")
            sort_order = sort_options.get("order", "desc")
            
            if sort_field == "overall_score":
                if sort_order == "desc":
                    query = query.order_by(EmployeeResult.overall_score.desc())
                else:
                    query = query.order_by(EmployeeResult.overall_score.asc())
            elif sort_field == "grade":
                if sort_order == "desc":
                    query = query.order_by(EmployeeResult.grade.desc())
                else:
                    query = query.order_by(EmployeeResult.grade.asc())
            elif sort_field == "name":
                if sort_order == "desc":
                    query = query.order_by(func.json_extract(EmployeeResult.employee_metadata, "$.name").desc())
                else:
                    query = query.order_by(func.json_extract(EmployeeResult.employee_metadata, "$.name").asc())
            
            # 총 개수 조회
            total = query.count()
            
            if total == 0:
                return EmployeeAIAnalysisList(
                    items=[], total=0, page=1, page_size=20, total_pages=1
                )
            
            # 페이지네이션 적용
            page = pagination.get("page", 1)
            page_size = pagination.get("page_size", 20)
            total_pages = (total + page_size - 1) // page_size
            
            offset = (page - 1) * page_size
            employees = query.offset(offset).limit(page_size).all()
            
            # EmployeeResult를 EmployeeAIAnalysisSummary로 변환
            employee_summaries = []
            for emp in employees:
                metadata = emp.employee_metadata or {}
                name = metadata.get("name", "Unknown")
                department = metadata.get("department", "미지정")
                position = metadata.get("position", "미지정")
                
                # 강점과 개선점 텍스트 생성
                ai_feedback = emp.ai_feedback or {}
                strengths = ai_feedback.get("strengths", [])
                improvements = ai_feedback.get("improvements", [])
                
                strengths_text = ", ".join(strengths[:2]) if strengths else "분석 중"
                improvements_text = ", ".join(improvements[:1]) if improvements else "분석 중" 
                ai_comment = ai_feedback.get("overall_comment", "")
                comment_preview = ai_comment[:100] + "..." if len(ai_comment) > 100 else ai_comment
                
                summary = EmployeeAIAnalysisSummary(
                    employee_id=emp.uid,
                    name=name,
                    department=department,
                    position=position,
                    ai_score=int(emp.overall_score),
                    grade=self._map_grade(emp.grade),
                    strengths_summary=strengths_text,
                    improvements_summary=improvements_text,
                    ai_comment_preview=comment_preview or "AI 분석 완료"
                )
                employee_summaries.append(summary)
            
            return EmployeeAIAnalysisList(
                items=employee_summaries,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
            
        except Exception as e:
            logger.error(f"직원 AI 분석 목록 조회 실패: {e}")
            return EmployeeAIAnalysisList(
                items=[], total=0, page=1, page_size=20, total_pages=1
            )
    
    def get_ai_recommendations(
        self,
        recommendation_type: str,
        limit: int = 10
    ) -> List[AIRecommendation]:
        """AI 추천 인재 조회"""
        try:
            # EmployeeResult 테이블에서 직접 조회
            employee_results = self.db.query(EmployeeResult).all()
            
            if not employee_results:
                return []
            
            recommendations = []
            
            if recommendation_type == RecommendationType.TALENT:
                # Top Talent: AI 점수 상위
                sorted_emps = sorted(
                    employee_results,
                    key=lambda x: float(x.overall_score or 0),
                    reverse=True
                )[:limit]
                
                for emp_result in sorted_emps:
                    metadata = emp_result.employee_metadata or {}
                    ai_feedback = emp_result.ai_feedback or {}
                    strengths = ai_feedback.get("strengths", [])[:3]
                    
                    rec = AIRecommendation(
                        employee_id=emp_result.uid,
                        name=metadata.get("name", "Unknown"),
                        department=metadata.get("department", "Unknown"),
                        position=metadata.get("position", "Unknown"),
                        recommendation_type=RecommendationType.TALENT,
                        recommendation_score=min(int(emp_result.overall_score or 0), 100),
                        recommendation_reason="탁월한 종합 역량과 높은 AI 평가 점수",
                        ai_score=int(emp_result.overall_score or 0),
                        grade=self._map_grade(emp_result.grade or "C"),
                        key_strengths=strengths
                    )
                    recommendations.append(rec)
                    
            elif recommendation_type == RecommendationType.PROMOTION:
                # 승진 후보: 리더십과 실행력이 높은 직원
                promotion_candidates = []
                for emp_result in employee_results:
                    dimension_scores = emp_result.dimension_scores or {}
                    leadership_score = dimension_scores.get("리더십", 0)
                    execution_score = dimension_scores.get("실행력", 0)
                    if int(leadership_score) >= 80 and int(execution_score) >= 80:
                        promotion_candidates.append(emp_result)
                            
                sorted_candidates = sorted(
                    promotion_candidates,
                    key=lambda x: float(x.overall_score or 0),
                    reverse=True
                )[:limit]
                
                for emp_result in sorted_candidates:
                    metadata = emp_result.employee_metadata or {}
                    ai_feedback = emp_result.ai_feedback or {}
                    strengths = ai_feedback.get("strengths", [])[:3]
                    
                    rec = AIRecommendation(
                        employee_id=emp_result.uid,
                        name=metadata.get("name", "Unknown"),
                        department=metadata.get("department", "Unknown"),
                        position=metadata.get("position", "Unknown"),
                        recommendation_type=RecommendationType.PROMOTION,
                        recommendation_score=int((emp_result.dimension_scores or {}).get("리더십", 0)),
                        recommendation_reason="뛰어난 리더십과 실행력으로 승진 준비 완료",
                        ai_score=int(emp_result.overall_score or 0),
                        grade=self._map_grade(emp_result.grade or "C"),
                        key_strengths=strengths
                    )
                    recommendations.append(rec)
                    
            elif recommendation_type == RecommendationType.RISK:
                # 이직 위험군: 점수가 낮거나 특정 패턴
                risk_employees = []
                for emp_result in employee_results:
                    score = int(emp_result.overall_score or 0)
                    if score < 70 or emp_result.grade in ["C", "D"]:
                        risk_employees.append(emp_result)
                        
                sorted_risks = sorted(
                    risk_employees,
                    key=lambda x: float(x.overall_score or 0)
                )[:limit]
                
                for emp_result in sorted_risks:
                    metadata = emp_result.employee_metadata or {}
                    ai_feedback = emp_result.ai_feedback or {}
                    improvements = ai_feedback.get("improvements", [])[:3]
                    
                    rec = AIRecommendation(
                        employee_id=emp_result.uid,
                        name=metadata.get("name", "Unknown"),
                        department=metadata.get("department", "Unknown"),
                        position=metadata.get("position", "Unknown"),
                        recommendation_type=RecommendationType.RISK,
                        recommendation_score=max(100 - int(emp_result.overall_score or 0), 0),
                        recommendation_reason="낮은 평가 점수와 개선 필요 영역 다수",
                        ai_score=int(emp_result.overall_score or 0),
                        grade=self._map_grade(emp_result.grade or "C"),
                        key_strengths=[],
                        risk_factors=improvements
                    )
                    recommendations.append(rec)
                    
            return recommendations
            
        except Exception as e:
            logger.error(f"AI 추천 리스트 조회 실패: {e}")
            return []
    
    def save_ai_feedback(
        self,
        employee_id: str,
        feedback_text: str,
        action: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """AI 피드백 저장"""
        try:
            # 피드백 저장 로직 (실제로는 별도 테이블 필요)
            feedback_id = f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 여기서는 로그만 남기고 성공 응답 반환
            logger.info(f"AI 피드백 저장: {employee_id} - {action}")
            
            return {
                "feedback_id": feedback_id,
                "saved_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"AI 피드백 저장 실패: {e}")
            raise
    
    def get_competency_radar_data(self, employee_id: str) -> Optional[CompetencyRadarData]:
        """직원의 역량 레이더 차트 데이터 조회"""
        try:
            analysis = self.get_employee_ai_analysis(employee_id)
            if not analysis:
                return None
                
            labels = [
                "실행력", "성장지향", "협업", "고객지향",
                "전문성", "혁신성", "리더십", "커뮤니케이션"
            ]
            
            values = [
                analysis.competencies.실행력,
                analysis.competencies.성장지향,
                analysis.competencies.협업,
                analysis.competencies.고객지향,
                analysis.competencies.전문성,
                analysis.competencies.혁신성,
                analysis.competencies.리더십,
                analysis.competencies.커뮤니케이션
            ]
            
            # 조직 평균 (실제로는 계산 필요)
            average_values = [75, 72, 78, 70, 73, 71, 74, 76]
            
            return CompetencyRadarData(
                labels=labels,
                values=values,
                average_values=average_values
            )
            
        except Exception as e:
            logger.error(f"역량 레이더 데이터 조회 실패: {e}")
            return None
    
    def get_dashboard_statistics(
        self,
        department: Optional[str] = None
    ) -> DashboardStatistics:
        """대시보드 통계 데이터 조회"""
        try:
            # EmployeeResult 테이블에서 직접 조회
            query = self.db.query(EmployeeResult)
            
            # 부서 필터링
            if department:
                query = query.filter(func.json_extract(EmployeeResult.employee_metadata, "$.department") == department)
            
            employee_results = query.all()
            
            if not employee_results:
                return self._empty_statistics()
                
            # 통계 계산
            total_employees = len(employee_results)
            
            # 등급 분포
            grade_distribution = {}
            scores = []
            for emp_result in employee_results:
                grade = emp_result.grade or "C"
                grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
                scores.append(int(emp_result.overall_score or 0))
                
            # 등급 비율
            grade_percentage = {
                grade: (count / total_employees * 100)
                for grade, count in grade_distribution.items()
            }
            
            # 점수 통계
            average_score = sum(scores) / len(scores) if scores else 0
            sorted_scores = sorted(scores)
            median_score = sorted_scores[len(sorted_scores) // 2] if sorted_scores else 0
            
            # 점수 구간
            score_range = {
                "900-1000": len([s for s in scores if 900 <= s <= 1000]),
                "800-899": len([s for s in scores if 800 <= s < 900]),
                "700-799": len([s for s in scores if 700 <= s < 800]),
                "600-699": len([s for s in scores if 600 <= s < 700]),
                "0-599": len([s for s in scores if s < 600])
            }
            
            # 역량 평균 계산
            competency_sums = {
                "실행력": 0, "성장지향": 0, "협업": 0, "고객지향": 0,
                "전문성": 0, "혁신성": 0, "리더십": 0, "커뮤니케이션": 0
            }
            
            for emp_result in employee_results:
                dimension_scores = emp_result.dimension_scores or {}
                for comp in competency_sums.keys():
                    score = dimension_scores.get(comp, 70)  # 기본값 70
                    competency_sums[comp] += int(score)
                    
            competency_averages = CompetencyScores(
                **{comp: int(total / total_employees) for comp, total in competency_sums.items()}
            )
            
            # 추천 인재 수 계산
            talent_count = len([e for e in employee_results if int(e.overall_score or 0) >= 85])
            promotion_candidates = len([
                e for e in employee_results
                if int((e.dimension_scores or {}).get("리더십", 0)) >= 80 and 
                   int((e.dimension_scores or {}).get("실행력", 0)) >= 80
            ])
            risk_employees = len([e for e in employee_results if e.grade in ["C", "D"]])
            
            return DashboardStatistics(
                total_employees=total_employees,
                grade_distribution=grade_distribution,
                grade_percentage=grade_percentage,
                average_score=average_score,
                median_score=median_score,
                score_range=score_range,
                competency_averages=competency_averages,
                top_strengths=[],  # 실제로는 계산 필요
                top_improvements=[],  # 실제로는 계산 필요
                talent_count=talent_count,
                promotion_candidates=promotion_candidates,
                risk_employees=risk_employees
            )
            
        except Exception as e:
            logger.error(f"대시보드 통계 조회 실패: {e}")
            return self._empty_statistics()
    
    def _empty_statistics(self) -> DashboardStatistics:
        """빈 통계 데이터 반환"""
        return DashboardStatistics(
            total_employees=0,
            grade_distribution={},
            grade_percentage={},
            average_score=0,
            median_score=0,
            score_range={},
            competency_averages=CompetencyScores(
                실행력=0, 성장지향=0, 협업=0, 고객지향=0,
                전문성=0, 혁신성=0, 리더십=0, 커뮤니케이션=0
            ),
            top_strengths=[],
            top_improvements=[],
            talent_count=0,
            promotion_candidates=0,
            risk_employees=0
        )