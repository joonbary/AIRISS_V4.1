# app/services/hybrid_analyzer.py
"""
AIRISS v4.0 하이브리드 분석기 - Python 3.13 완전 호환 버전
텍스트 + 정량 데이터 통합 분석 + 편향 탐지 + 조건부 영구 저장
"""

import pandas as pd
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import uuid

from app.services.text_analyzer import AIRISSTextAnalyzer
from app.services.quantitative_analyzer import QuantitativeAnalyzer

logger = logging.getLogger(__name__)

class AIRISSHybridAnalyzer:
    """텍스트 + 정량 통합 분석기 with 편향 탐지 + 안전한 영구 저장"""
    
    def __init__(self):
        self.text_analyzer = AIRISSTextAnalyzer()
        self.quantitative_analyzer = QuantitativeAnalyzer()
        
        # 편향 탐지 시스템 초기화
        self.bias_detector = None
        try:
            from app.services.bias_detection import BiasDetector
            self.bias_detector = BiasDetector()
            logger.info("✅ 편향 탐지 시스템 로드 완료")
        except ImportError:
            logger.warning("⚠️ 편향 탐지 모듈 없음 - 기본 분석만 수행")
        except Exception as e:
            logger.warning(f"⚠️ 편향 탐지 시스템 로드 실패: {e}")
        
        # 🔥 Python 3.13 호환: 완전한 조건부 저장 서비스 초기화
        self.storage_service = None
        self.storage_available = False
        
        try:
            # 단계별 안전한 import
            logger.info("🔄 저장 서비스 로드 시도...")
            from app.services.analysis_storage_service import storage_service
            
            # 서비스 가용성 확인
            if hasattr(storage_service, 'is_available') and storage_service.is_available():
                self.storage_service = storage_service
                self.storage_available = True
                logger.info("✅ 분석 결과 저장 서비스 로드 완료")
            else:
                logger.warning("⚠️ 저장 서비스가 비활성화 상태")
                
        except ImportError as e:
            logger.warning(f"⚠️ 저장 서비스 모듈 없음: {e}")
        except Exception as e:
            logger.warning(f"⚠️ 저장 서비스 초기화 실패 (Python 3.13 호환성): {e}")
            logger.info("📝 메모리 기반 분석만 수행됩니다")
        
        # 통합 가중치
        self.hybrid_weights = {
            'text_analysis': 0.6,
            'quantitative_analysis': 0.4
        }
        
        # 분석 결과 저장 (편향 탐지용) - 항상 사용 가능한 메모리 저장소
        self.analysis_history = []
        
        # 초기화 상태 로깅
        logger.info(f"✅ AIRISS v4.0 하이브리드 분석기 초기화 완료")
        logger.info(f"   📊 편향 탐지: {'활성화' if self.bias_detector else '비활성화'}")
        logger.info(f"   💾 영구 저장: {'활성화' if self.storage_available else '비활성화 (메모리만)'}")
    
    def comprehensive_analysis(self, 
                             uid: str, 
                             opinion: str, 
                             row_data: pd.Series,
                             save_to_storage: bool = True,
                             file_id: Optional[str] = None,
                             filename: Optional[str] = None) -> Dict[str, Any]:
        """종합 분석: 텍스트 + 정량 + 편향 체크 + 안전한 영구 저장"""
        
        # 1. 텍스트 분석
        text_results = {}
        for dimension in self.text_analyzer.framework.keys():
            text_results[dimension] = self.text_analyzer.analyze_text(opinion, dimension)
        
        text_overall = self.text_analyzer.calculate_overall_score(
            {dim: result["score"] for dim, result in text_results.items()}
        )
        
        # 2. 정량 분석
        quant_data = self.quantitative_analyzer.extract_quantitative_data(row_data)
        quant_results = self.quantitative_analyzer.calculate_quantitative_score(quant_data)
        
        # 3. 하이브리드 점수 계산
        text_weight = self.hybrid_weights['text_analysis']
        quant_weight = self.hybrid_weights['quantitative_analysis']
        
        # 데이터 품질에 따른 가중치 조정
        if quant_results["data_quality"] == "없음":
            text_weight = 0.8
            quant_weight = 0.2
        elif quant_results["data_quality"] == "낮음":
            text_weight = 0.7
            quant_weight = 0.3
        elif quant_results["data_quality"] == "높음":
            text_weight = 0.5
            quant_weight = 0.5
        
        hybrid_score = (
            text_overall["overall_score"] * text_weight + 
            quant_results["quantitative_score"] * quant_weight
        )
        
        # 4. 통합 신뢰도
        hybrid_confidence = (
            text_overall.get("confidence", 70) * text_weight + 
            quant_results["confidence"] * quant_weight
        )
        
        # 5. 하이브리드 등급
        hybrid_grade_info = self._calculate_hybrid_grade(hybrid_score)
        
        # 6. 설명가능성 정보 추가
        explainability_info = self._generate_explainability(
            text_results, quant_results, text_weight, quant_weight, hybrid_score
        )
        
        # 7. 분석 결과 저장 (편향 탐지용)
        if hasattr(row_data, 'to_dict'):
            analysis_record = {
                'uid': uid,
                'hybrid_score': hybrid_score,
                'timestamp': datetime.now()
            }
            # 보호 속성 추가 (있는 경우)
            for attr in ['성별', '연령대', '부서', '직급']:
                if attr in row_data:
                    analysis_record[attr] = row_data[attr]
            self.analysis_history.append(analysis_record)
        
        # 8. 분석 결과 구성
        analysis_result = {
            "text_analysis": {
                "overall_score": text_overall["overall_score"],
                "grade": text_overall["grade"],
                "dimension_scores": {dim: result["score"] for dim, result in text_results.items()},
                "dimension_details": text_results
            },
            "quantitative_analysis": quant_results,
            "hybrid_analysis": {
                "overall_score": round(hybrid_score, 1),
                "grade": hybrid_grade_info["grade"],
                "grade_description": hybrid_grade_info["grade_description"],
                "percentile": hybrid_grade_info["percentile"],
                "confidence": round(hybrid_confidence, 1),
                "analysis_composition": {
                    "text_weight": round(text_weight * 100, 1),
                    "quantitative_weight": round(quant_weight * 100, 1)
                }
            },
            "explainability": explainability_info,
            "analysis_metadata": {
                "uid": uid,
                "analysis_version": "AIRISS v4.0 - Hybrid Enhanced (Python 3.13 Compatible)",
                "data_sources": {
                    "text_available": bool(opinion and opinion.strip()),
                    "quantitative_available": bool(quant_data),
                    "quantitative_data_quality": quant_results["data_quality"]
                },
                "bias_detection_available": self.bias_detector is not None,
                "storage_available": self.storage_available
            }
        }
        
        # 9. 영구 저장 (조건부 안전한 저장)
        if save_to_storage:
            storage_result = self._safe_save_to_storage(
                uid, file_id, filename, opinion, hybrid_score, 
                text_overall, quant_results, hybrid_grade_info, hybrid_confidence, text_results
            )
            analysis_result["storage_info"] = storage_result
        
        return analysis_result
    
    def _safe_save_to_storage(self, uid, file_id, filename, opinion, hybrid_score,
                            text_overall, quant_results, hybrid_grade_info, hybrid_confidence, text_results):
        """안전한 저장 처리 (Python 3.13 호환)"""
        
        if not self.storage_available or not self.storage_service:
            return {
                "storage_enabled": False,
                "message": "저장 서비스 비활성화 - 메모리에만 저장됨",
                "reason": "python_313_compatibility"
            }
        
        try:
            storage_data = {
                "uid": uid,
                "file_id": file_id or str(uuid.uuid4()),
                "filename": filename or "unknown",
                "opinion": opinion,
                "hybrid_score": hybrid_score,
                "text_score": text_overall["overall_score"],
                "quantitative_score": quant_results["quantitative_score"],
                "ok_grade": hybrid_grade_info["grade"],
                "grade_description": hybrid_grade_info["grade_description"],
                "confidence": hybrid_confidence,
                "dimension_scores": {dim: result["score"] for dim, result in text_results.items()},
                "analysis_mode": "hybrid",
                "version": "4.0"
            }
            
            analysis_id = self.storage_service.save_analysis_result(storage_data)
            
            return {
                "analysis_id": analysis_id,
                "saved_at": datetime.now().isoformat(),
                "storage_enabled": True,
                "storage_mode": "persistent"
            }
            
        except Exception as e:
            logger.error(f"❌ 분석 결과 저장 실패: {e}")
            
            # 메모리 저장소에라도 저장
            memory_id = f"mem_{uid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return {
                "analysis_id": memory_id,
                "error": str(e),
                "storage_enabled": False,
                "storage_mode": "memory_fallback",
                "message": "영구 저장 실패 - 메모리에만 저장됨"
            }
    
    def save_analysis_job(self, job_info: Dict[str, Any]) -> Optional[str]:
        """분석 작업 정보 저장 (안전한 처리)"""
        if not self.storage_available or not self.storage_service:
            logger.info("저장 서비스 비활성화 - 작업 정보 저장 건너뜀")
            return None
        
        try:
            job_id = self.storage_service.save_analysis_job(job_info)
            logger.info(f"✅ 분석 작업 정보 저장 완료: {job_id}")
            return job_id
        except Exception as e:
            logger.error(f"❌ 분석 작업 정보 저장 실패: {e}")
            return None
    
    def get_stored_analysis_results(self, 
                                  file_id: Optional[str] = None,
                                  uid: Optional[str] = None,
                                  limit: int = 100) -> List[Dict[str, Any]]:
        """저장된 분석 결과 조회 (안전한 처리)"""
        if not self.storage_available or not self.storage_service:
            logger.info("저장 서비스 비활성화 - 빈 결과 반환")
            return []
        
        try:
            results = self.storage_service.get_analysis_results(
                file_id=file_id,
                uid=uid,
                limit=limit
            )
            return results
        except Exception as e:
            logger.error(f"❌ 분석 결과 조회 실패: {e}")
            return []
    
    def get_analysis_statistics(self, days: int = 30) -> Dict[str, Any]:
        """분석 통계 조회 (안전한 처리)"""
        if not self.storage_available or not self.storage_service:
            return {
                "message": "저장 서비스 비활성화",
                "memory_analysis_count": len(self.analysis_history),
                "storage_mode": "memory_only"
            }
        
        try:
            stats = self.storage_service.get_analysis_statistics(days=days)
            return stats
        except Exception as e:
            logger.error(f"❌ 분석 통계 조회 실패: {e}")
            return {
                "error": str(e),
                "memory_analysis_count": len(self.analysis_history),
                "storage_mode": "error_fallback"
            }
    
    def _calculate_hybrid_grade(self, score: float) -> Dict[str, str]:
        """하이브리드 점수를 7단계 등급으로 변환 (S, A+, A, B+, B, C, D)"""
        if score >= 95:
            return {
                "grade": "S",
                "grade_description": "탁월함 (Superb) - 전사 TOP 1%",
                "percentile": "상위 1%"
            }
        elif score >= 90:
            return {
                "grade": "A+",
                "grade_description": "매우 우수 (Excellent) - 전사 TOP 5%",
                "percentile": "상위 5%"
            }
        elif score >= 80:
            return {
                "grade": "A",
                "grade_description": "우수 (Outstanding) - 전사 TOP 15%",
                "percentile": "상위 15%"
            }
        elif score >= 70:
            return {
                "grade": "B+",
                "grade_description": "양호 (Good) - 전사 TOP 30%",
                "percentile": "상위 30%"
            }
        elif score >= 60:
            return {
                "grade": "B",
                "grade_description": "보통 (Average) - 전사 TOP 50%",
                "percentile": "상위 50%"
            }
        elif score >= 50:
            return {
                "grade": "C",
                "grade_description": "개선 필요 (Needs Improvement) - 전사 TOP 70%",
                "percentile": "상위 70%"
            }
        else:
            return {
                "grade": "D",
                "grade_description": "집중 관리 필요 (Requires Attention) - 하위 30%",
                "percentile": "하위 30%"
            }
    
    def _generate_explainability(self, 
                               text_results: Dict,
                               quant_results: Dict,
                               text_weight: float,
                               quant_weight: float,
                               hybrid_score: float) -> Dict[str, Any]:
        """점수 산출 근거 설명 생성"""
        
        # 주요 긍정/부정 요인 추출
        positive_factors = []
        negative_factors = []
        
        # 텍스트 분석 요인
        for dimension, result in text_results.items():
            if result['score'] >= 80:
                positive_factors.append({
                    'factor': f"{dimension}",
                    'score': result['score'],
                    'impact': result['score'] * self.text_analyzer.framework[dimension]['weight'] * text_weight,
                    'evidence': result['signals']['positive_words'][:3]
                })
            elif result['score'] < 60:
                negative_factors.append({
                    'factor': f"{dimension}",
                    'score': result['score'],
                    'impact': (100 - result['score']) * self.text_analyzer.framework[dimension]['weight'] * text_weight,
                    'evidence': result['signals']['negative_words'][:3]
                })
        
        # 정량 분석 요인
        if quant_results['quantitative_score'] >= 80:
            positive_factors.append({
                'factor': "정량적 성과",
                'score': quant_results['quantitative_score'],
                'impact': quant_results['quantitative_score'] * quant_weight,
                'evidence': ["KPI 달성", "성과 우수"]
            })
        elif quant_results['quantitative_score'] < 60:
            negative_factors.append({
                'factor': "정량적 성과",
                'score': quant_results['quantitative_score'],
                'impact': (100 - quant_results['quantitative_score']) * quant_weight,
                'evidence': ["KPI 미달", "성과 부진"]
            })
        
        # 상위 3개 요인 정렬
        positive_factors.sort(key=lambda x: x['impact'], reverse=True)
        negative_factors.sort(key=lambda x: x['impact'], reverse=True)
        
        return {
            "score_breakdown": {
                "text_contribution": round(text_results.get('업무성과', {}).get('score', 50) * text_weight, 1),
                "quantitative_contribution": round(quant_results['quantitative_score'] * quant_weight, 1),
                "final_score": round(hybrid_score, 1)
            },
            "key_positive_factors": positive_factors[:3],
            "key_negative_factors": negative_factors[:3],
            "improvement_suggestions": self._generate_improvement_suggestions(negative_factors),
            "confidence_explanation": self._explain_confidence(text_results, quant_results)
        }
    
    def _generate_improvement_suggestions(self, negative_factors: List[Dict]) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        for factor in negative_factors[:3]:
            if factor['factor'] == "커뮤니케이션":
                suggestions.append("💡 커뮤니케이션 스킬 향상 교육 참여를 권장합니다.")
            elif factor['factor'] == "리더십협업":
                suggestions.append("💡 팀워크 및 협업 역량 강화 프로그램 참여를 고려하세요.")
            elif factor['factor'] == "전문성학습":
                suggestions.append("💡 직무 관련 전문 교육 및 자격증 취득을 추천합니다.")
            elif factor['factor'] == "업무성과":
                suggestions.append("💡 목표 설정 및 시간 관리 기법 학습이 도움될 것입니다.")
            elif factor['factor'] == "정량적 성과":
                suggestions.append("💡 KPI 달성을 위한 구체적인 실행 계획 수립이 필요합니다.")
        
        return suggestions[:3]  # 최대 3개 제안
    
    def _explain_confidence(self, text_results: Dict, quant_results: Dict) -> str:
        """신뢰도 설명"""
        avg_text_confidence = sum(r.get('confidence', 0) for r in text_results.values()) / len(text_results)
        quant_confidence = quant_results.get('confidence', 0)
        
        if avg_text_confidence >= 80 and quant_confidence >= 80:
            return "높은 신뢰도: 충분한 텍스트 정보와 정량 데이터를 기반으로 분석되었습니다."
        elif avg_text_confidence >= 60 or quant_confidence >= 60:
            return "중간 신뢰도: 일부 데이터가 제한적이지만 의미있는 분석이 가능했습니다."
        else:
            return "낮은 신뢰도: 제한된 정보로 인해 추가 데이터 수집을 권장합니다."
    
    def detect_bias_in_batch(self, analysis_results_df: pd.DataFrame) -> Dict[str, Any]:
        """배치 분석 결과의 편향 탐지 (안전한 처리)"""
        if not self.bias_detector:
            return {
                "error": "편향 탐지 시스템이 설치되지 않았습니다.",
                "recommendation": "bias_detection 모듈을 설치하세요."
            }
        
        try:
            bias_report = self.bias_detector.detect_bias(analysis_results_df)
            return bias_report
        except Exception as e:
            logger.error(f"편향 탐지 오류: {e}")
            return {
                "error": f"편향 탐지 중 오류 발생: {str(e)}",
                "recommendation": "데이터 형식을 확인하세요."
            }
    
    def get_fairness_metrics(self) -> Dict[str, Any]:
        """현재까지 분석된 데이터의 공정성 메트릭"""
        if not self.analysis_history:
            return {
                "status": "no_data",
                "message": "아직 분석된 데이터가 없습니다."
            }
        
        df = pd.DataFrame(self.analysis_history)
        
        metrics = {
            "total_analyzed": len(df),
            "average_score": round(df['hybrid_score'].mean(), 1),
            "score_std": round(df['hybrid_score'].std(), 1),
            "score_distribution": {
                "min": round(df['hybrid_score'].min(), 1),
                "25%": round(df['hybrid_score'].quantile(0.25), 1),
                "50%": round(df['hybrid_score'].quantile(0.50), 1),
                "75%": round(df['hybrid_score'].quantile(0.75), 1),
                "max": round(df['hybrid_score'].max(), 1)
            },
            "storage_info": {
                "storage_available": self.storage_available,
                "memory_records": len(self.analysis_history)
            }
        }
        
        # 보호 속성별 평균 점수
        for attr in ['성별', '연령대', '부서', '직급']:
            if attr in df.columns:
                metrics[f'{attr}_averages'] = df.groupby(attr)['hybrid_score'].mean().to_dict()
        
        return metrics
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "version": "AIRISS v4.0 - Python 3.13 Compatible",
            "components": {
                "text_analyzer": True,
                "quantitative_analyzer": True,
                "bias_detector": self.bias_detector is not None,
                "storage_service": self.storage_available
            },
            "analysis_count": len(self.analysis_history),
            "storage_mode": "persistent" if self.storage_available else "memory_only",
            "python_version_compatible": True
        }
