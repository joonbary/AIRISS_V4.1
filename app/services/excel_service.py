"""Excel 보고서 생성 서비스"""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import logging

from app.core.analyzers.framework import AIRISS_FRAMEWORK
from app.services.analysis_storage_service import storage_service

logger = logging.getLogger(__name__)


class ExcelReportService:
    """Excel 보고서 생성 서비스"""
    
    async def create_report(
        self,
        job_id: str,
        results: List[Dict[str, Any]],
        enable_ai: bool = False,
        analysis_mode: str = "hybrid",
        hybrid_stats: Dict[str, Any] = {}
    ) -> str:
        """AIRISS v4.0 Excel 보고서 생성 (DB에서 직접 결과 조회)"""
        try:
            # 결과 디렉토리 생성
            os.makedirs('results', exist_ok=True)

            # 🔥 DB에서 최신 결과 직접 조회 (results 파라미터 무시)
            db_results = storage_service.get_analysis_results(file_id=job_id)
            if db_results:
                df_results = pd.DataFrame(db_results)
            else:
                df_results = pd.DataFrame(results)

            # AI 피드백 컬럼 누락 방지: 항상 포함 및 명확한 기본값
            ai_feedback_columns = [
                ("ai_strengths", "N/A"),
                ("ai_weaknesses", "N/A"),
                ("ai_feedback", "N/A"),
                ("ai_recommendations", [])
            ]
            for col, default in ai_feedback_columns:
                if col not in df_results.columns:
                    df_results[col] = default
                else:
                    # 결측값/None/빈값 처리
                    if col == "ai_recommendations":
                        df_results[col] = df_results[col].apply(lambda x: x if isinstance(x, list) and x else [])
                    else:
                        df_results[col] = df_results[col].fillna(default).replace('', default)
            # 컬럼 순서 보장 (주요 컬럼 + AI 피드백)
            preferred_order = [
                "uid", "filename", "opinion", "hybrid_score", "text_score", "quantitative_score", "ok_grade", "grade_description", "confidence", "dimension_scores",
                "ai_strengths", "ai_weaknesses", "ai_feedback", "ai_recommendations", "analysis_mode", "version", "created_at", "updated_at"
            ]
            ordered_cols = [col for col in preferred_order if col in df_results.columns] + [col for col in df_results.columns if col not in preferred_order]
            df_results = df_results[ordered_cols]

            # OK등급별 분포 계산
            grade_distribution = df_results["ok_grade"].value_counts() if "ok_grade" in df_results.columns else []

            # 통계 요약 생성
            summary_stats = self._create_summary_stats(df_results, df_results.to_dict('records'), analysis_mode, hybrid_stats, grade_distribution)
            df_summary = pd.DataFrame(summary_stats)

            # 파일명 생성
            ai_suffix = "_AI완전분석" if enable_ai else "_하이브리드분석"
            mode_suffix = f"_{analysis_mode}모드"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_path = f'results/OK금융그룹_AIRISS_v4.0{mode_suffix}{ai_suffix}_{timestamp}.xlsx'

            # Excel 파일 생성
            with pd.ExcelWriter(result_path, engine='openpyxl') as writer:
                # 메인 결과 시트
                df_results.to_excel(writer, index=False, sheet_name='AIRISS_v4.0_분석결과')
                # 통계 요약 시트
                df_summary.to_excel(writer, index=False, sheet_name='v4.0_통계요약')
                # 8대 영역별 상세 시트
                dimension_analysis = self._create_dimension_analysis(df_results)
                df_dimensions = pd.DataFrame(dimension_analysis)
                df_dimensions.to_excel(writer, index=False, sheet_name='영역별_분석')
                # 하이브리드 분석 상세 시트
                hybrid_analysis = self._create_hybrid_analysis(df_results)
                df_hybrid = pd.DataFrame(hybrid_analysis)
                df_hybrid.to_excel(writer, index=False, sheet_name='하이브리드_비교분석')

            logger.info(f"AIRISS v4.0 Excel 보고서 생성 완료: {result_path}")
            return result_path
        except Exception as e:
            logger.error(f"Excel 보고서 생성 오류: {e}")
            raise
    
    def _create_summary_stats(
        self,
        df_results: pd.DataFrame,
        results: List[Dict],
        analysis_mode: str,
        hybrid_stats: Dict,
        grade_distribution: pd.Series
    ) -> List[Dict[str, Any]]:
        """통계 요약 데이터 생성"""
        summary_stats = []
        summary_stats.append({
            "항목": "AIRISS 버전",
            "값": "v4.0 마이크로서비스",
            "설명": "텍스트 + 정량데이터 통합분석 API 서버"
        })
        summary_stats.append({
            "항목": "전체 분석 건수",
            "값": len(results),
            "설명": "총 분석된 직원 수"
        })
        summary_stats.append({
            "항목": "분석 모드",
            "값": analysis_mode,
            "설명": "적용된 분석 방식"
        })
        # 안전하게 평균 하이브리드 점수 계산
        if "hybrid_score" in df_results.columns and not df_results.empty:
            avg_hybrid = round(df_results["hybrid_score"].mean(), 1)
        else:
            avg_hybrid = 0
        summary_stats.append({
            "항목": "평균 하이브리드 점수",
            "값": avg_hybrid,
            "설명": "전체 직원 평균 통합 점수"
        })
        if "quant_data_count" in df_results.columns and not df_results.empty:
            avg_quant_data = round(df_results["quant_data_count"].mean(), 1)
            summary_stats.append({
                "항목": "평균 정량데이터 수",
                "값": avg_quant_data,
                "설명": "개인당 평균 정량데이터 개수"
            })
        if hybrid_stats.get("quantitative_usage_rate"):
            summary_stats.append({
                "항목": "정량데이터 활용률",
                "값": f"{hybrid_stats['quantitative_usage_rate']}%",
                "설명": "정량데이터가 포함된 분석 비율"
            })
        # OK등급별 분포
        if isinstance(grade_distribution, pd.Series) and not df_results.empty:
            for grade, count in grade_distribution.items():
                percentage = (count / len(results)) * 100 if len(results) > 0 else 0
                summary_stats.append({
                    "항목": f"{grade} 등급",
                    "값": f"{count}명 ({percentage:.1f}%)",
                    "설명": f"{grade} 등급 직원 수 (하이브리드 기준)"
                })
        return summary_stats
    
    def _create_dimension_analysis(self, df_results: pd.DataFrame) -> List[Dict[str, Any]]:
        """8대 영역별 분석 데이터 생성"""
        dimension_analysis = []
        
        # dimension_scores가 문자열로 저장되어 있으므로 파싱 필요
        for dimension in AIRISS_FRAMEWORK.keys():
            dimension_info = AIRISS_FRAMEWORK[dimension]
            
            # 각 행의 dimension_scores에서 해당 차원 점수 추출
            scores = []
            for idx, row in df_results.iterrows():
                try:
                    dim_scores = eval(row.get("dimension_scores", "{}"))
                    score = dim_scores.get(dimension, 50)
                    scores.append(score)
                except:
                    scores.append(50)
            
            scores = pd.Series(scores)
            
            dimension_analysis.append({
                "영역": dimension,
                "아이콘": dimension_info['icon'],
                "가중치": f"{dimension_info['weight']*100}%",
                "설명": dimension_info['description'],
                "평균점수": round(scores.mean(), 1),
                "최고점수": round(scores.max(), 1),
                "최저점수": round(scores.min(), 1),
                "표준편차": round(scores.std(), 1),
                "우수자수": len(scores[scores >= 80]),
                "개선필요자수": len(scores[scores < 60])
            })
        
        return dimension_analysis
    
    def _create_hybrid_analysis(self, df_results: pd.DataFrame) -> List[Dict[str, Any]]:
        """하이브리드 분석 비교 데이터 생성"""
        hybrid_analysis = []
        
        if "hybrid_score" in df_results.columns and "text_total_score" in df_results.columns:
            hybrid_scores = df_results["hybrid_score"]
            text_scores = df_results["text_total_score"]
            quant_scores = df_results["quant_total_score"] if "quant_total_score" in df_results.columns else pd.Series([50] * len(df_results))
            
            hybrid_analysis.append({
                "분석유형": "하이브리드 통합",
                "평균점수": round(hybrid_scores.mean(), 1),
                "최고점수": round(hybrid_scores.max(), 1),
                "최저점수": round(hybrid_scores.min(), 1),
                "표준편차": round(hybrid_scores.std(), 1),
                "신뢰도": "높음 (다중소스)"
            })
            
            hybrid_analysis.append({
                "분석유형": "텍스트 분석",
                "평균점수": round(text_scores.mean(), 1),
                "최고점수": round(text_scores.max(), 1),
                "최저점수": round(text_scores.min(), 1),
                "표준편차": round(text_scores.std(), 1),
                "신뢰도": "중간 (키워드 기반)"
            })
            
            hybrid_analysis.append({
                "분석유형": "정량 분석",
                "평균점수": round(quant_scores.mean(), 1),
                "최고점수": round(quant_scores.max(), 1),
                "최저점수": round(quant_scores.min(), 1),
                "표준편차": round(quant_scores.std(), 1),
                "신뢰도": "높음 (객관적 데이터)"
            })
        
        return hybrid_analysis