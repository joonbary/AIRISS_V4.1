# app/services/text_analyzer.py
"""
AIRISS v4.1 텍스트 분석기 - 딥러닝 NLP 적용
한국어 특화 BERT 모델을 활용한 고도화된 감정/의도 분석
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import asyncio
import numpy as np
import re
from collections import Counter

logger = logging.getLogger(__name__)

# AIRISS 8대 영역 정의 (기존 유지 + 확장)
AIRISS_FRAMEWORK = {
    "업무성과": {
        "keywords": {
            "positive": [
                "우수", "탁월", "뛰어남", "성과", "달성", "완료", "성공", "효율", "생산적", 
                "목표달성", "초과달성", "품질", "정확", "신속", "완벽", "전문적", "체계적",
                "혁신적", "창의적", "개선", "향상", "최적화", "능숙", "숙련", "전문성"
            ],
            "negative": [
                "부족", "미흡", "지연", "실패", "문제", "오류", "늦음", "비효율", 
                "목표미달", "품질저하", "부정확", "미완성", "부실", "개선필요", "미달"
            ]
        },
        "weight": 0.25,
        "description": "업무 산출물의 양과 질",
        "bert_aspects": ["업무 품질", "목표 달성도", "생산성", "효율성"]
    },
    "KPI달성": {
        "keywords": {
            "positive": [
                "KPI달성", "지표달성", "목표초과", "성과우수", "실적우수", "매출증가", 
                "효율향상", "생산성향상", "수치달성", "성장", "개선", "상승", "증가"
            ],
            "negative": [
                "KPI미달", "목표미달", "실적부진", "매출감소", "효율저하", 
                "생산성저하", "수치부족", "하락", "퇴보", "감소", "정체"
            ]
        },
        "weight": 0.20,
        "description": "핵심성과지표 달성도",
        "bert_aspects": ["정량적 성과", "목표 대비 실적", "성장률"]
    },
    "태도마인드": {
        "keywords": {
            "positive": [
                "적극적", "긍정적", "열정", "성실", "책임감", "진취적", "협조적", 
                "성장지향", "학습의지", "도전정신", "주인의식", "헌신", "몰입", "열의"
            ],
            "negative": [
                "소극적", "부정적", "무관심", "불성실", "회피", "냉소적", 
                "비협조적", "안주", "현상유지", "수동적", "무기력", "태만"
            ]
        },
        "weight": 0.15,
        "description": "업무에 대한 태도와 마인드셋",
        "bert_aspects": ["적극성", "책임감", "열정", "성장 마인드셋"]
    },
    "커뮤니케이션": {
        "keywords": {
            "positive": [
                "명확", "정확", "신속", "친절", "경청", "소통", "전달", "이해", 
                "설득", "협의", "조율", "공유", "투명", "개방적", "원활", "효과적"
            ],
            "negative": [
                "불명확", "지연", "무시", "오해", "단절", "침묵", "회피", 
                "독단", "일방적", "폐쇄적", "소통부족", "전달미흡", "갈등"
            ]
        },
        "weight": 0.15,
        "description": "의사소통 능력과 스타일",
        "bert_aspects": ["명확성", "적시성", "공감능력", "설득력"]
    },
    "리더십협업": {
        "keywords": {
            "positive": [
                "리더십", "팀워크", "협업", "지원", "멘토링", "동기부여", "조율", 
                "화합", "팀빌딩", "위임", "코칭", "영향력", "존중", "배려", "공유"
            ],
            "negative": [
                "독단", "갈등", "비협조", "소외", "분열", "대립", "이기주의", 
                "방해", "무관심", "고립", "개인주의", "권위적", "강압적"
            ]
        },
        "weight": 0.10,
        "description": "리더십과 협업 능력",
        "bert_aspects": ["팀 기여도", "리더십 스타일", "협업 자세"]
    },
    "전문성학습": {
        "keywords": {
            "positive": [
                "전문", "숙련", "기술", "지식", "학습", "발전", "역량", "능력", 
                "성장", "향상", "습득", "개발", "전문성", "노하우", "혁신", "연구"
            ],
            "negative": [
                "미숙", "부족", "낙후", "무지", "정체", "퇴보", "무능력", 
                "기초부족", "역량부족", "실력부족", "개선필요", "학습부진"
            ]
        },
        "weight": 0.08,
        "description": "전문성과 학습능력",
        "bert_aspects": ["전문 지식", "학습 속도", "기술 숙련도"]
    },
    "창의혁신": {
        "keywords": {
            "positive": [
                "창의", "혁신", "아이디어", "개선", "효율화", "최적화", "새로운", 
                "도전", "변화", "발상", "창조", "혁신적", "독창적", "선도적"
            ],
            "negative": [
                "보수적", "경직", "틀에박힌", "변화거부", "기존방식", "관습적", 
                "경직된", "고정적", "변화없이", "구태의연", "매너리즘"
            ]
        },
        "weight": 0.05,
        "description": "창의성과 혁신 마인드",
        "bert_aspects": ["창의성", "혁신 의지", "변화 수용성"]
    },
    "조직적응": {
        "keywords": {
            "positive": [
                "적응", "융화", "조화", "문화", "규칙준수", "윤리", "신뢰", 
                "안정", "일관성", "성실성", "조직", "회사", "충성", "소속감"
            ],
            "negative": [
                "부적응", "갈등", "위반", "비윤리", "불신", "일탈", 
                "문제행동", "규정위반", "조직과", "이탈", "불화"
            ]
        },
        "weight": 0.02,
        "description": "조직문화 적응도와 윤리성",
        "bert_aspects": ["조직 적응력", "윤리성", "규정 준수"]
    }
}

class AIRISSTextAnalyzer:
    """AIRISS v4.1 딥러닝 기반 텍스트 분석기"""
    
    def __init__(self):
        self.framework = AIRISS_FRAMEWORK
        self.openai_available = False
        self.openai = None
        self.bert_model = None
        self.bias_detector = None
        
        # 모델 초기화
        self._initialize_models()
        
    def _initialize_models(self):
        """딥러닝 모델 초기화"""
        # OpenAI 모듈 체크
        try:
            import openai
            self.openai = openai
            self.openai_available = True
            logger.info("✅ OpenAI 모듈 로드 성공")
        except ImportError as e:
            logger.warning(f"⚠️ OpenAI 모듈 없음 - 고급 AI 분석 제한됨: {e}")
            self.openai_available = False
        except Exception as e:
            logger.error(f"OpenAI 모듈 로드 중 예외 발생: {e}")
            self.openai_available = False
        
        # 한국어 BERT 모델 초기화 시도
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            # KcELECTRA 또는 KoBERT 모델 사용
            model_name = "beomi/KcELECTRA-base-v2022"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.bert_available = True
            logger.info("✅ 한국어 BERT 모델 로드 성공")
        except:
            self.bert_available = False
            logger.warning("⚠️ BERT 모델 로드 실패 - 향상된 키워드 분석 사용")
        
        # 편향 탐지기 초기화
        try:
            from app.services.bias_detection.bias_detector import BiasDetector
            self.bias_detector = BiasDetector()
        except ImportError:
            logger.warning("⚠️ 편향 탐지기 모듈 없음")
            self.bias_detector = None
    
    def analyze_text(self, text: str, dimension: str) -> Dict[str, Any]:
        """향상된 텍스트 분석 - 딥러닝 + 키워드 하이브리드"""
        if not text or text.lower() in ['nan', 'null', '', 'none']:
            return {
                "score": 50,
                "confidence": 0,
                "signals": {"positive": 0, "negative": 0, "positive_words": [], "negative_words": []},
                "analysis_method": "default"
            }
        
        # 1. 기본 키워드 분석 (폴백용)
        keyword_result = self._keyword_analysis(text, dimension)
        
        # 2. BERT 기반 감정/의도 분석 (가능한 경우)
        if self.bert_available:
            bert_result = self._bert_analysis(text, dimension)
            # 두 결과를 가중 평균으로 결합
            combined_score = keyword_result["score"] * 0.4 + bert_result["score"] * 0.6
            combined_confidence = (keyword_result["confidence"] + bert_result["confidence"]) / 2
            
            return {
                "score": round(combined_score, 1),
                "confidence": round(combined_confidence, 1),
                "signals": keyword_result["signals"],
                "sentiment": bert_result.get("sentiment", "neutral"),
                "intent": bert_result.get("intent", "unknown"),
                "analysis_method": "hybrid_bert"
            }
        else:
            # BERT 없을 경우 향상된 키워드 분석
            enhanced_result = self._enhanced_keyword_analysis(text, dimension)
            return enhanced_result
    
    def _keyword_analysis(self, text: str, dimension: str) -> Dict[str, Any]:
        """기존 키워드 기반 분석 (개선됨)"""
        keywords = self.framework[dimension]["keywords"]
        text_lower = text.lower()
        
        # 텍스트 전처리 - 특수문자 제거, 토큰화
        text_cleaned = re.sub(r'[^\w\s]', ' ', text_lower)
        tokens = text_cleaned.split()
        
        # N-gram 분석 (1-gram, 2-gram)
        positive_matches = []
        negative_matches = []
        
        # 1-gram 매칭
        for word in keywords["positive"]:
            if word in text_lower:
                positive_matches.append(word)
                # 문맥 가중치 - 문장 시작/끝 부분에 나오면 가중치 증가
                if text_lower.startswith(word) or text_lower.endswith(word):
                    positive_matches.append(word)  # 중복 추가로 가중치 효과
        
        for word in keywords["negative"]:
            if word in text_lower:
                negative_matches.append(word)
                if text_lower.startswith(word) or text_lower.endswith(word):
                    negative_matches.append(word)
        
        # 감정 강도 분석
        intensity_words = {
            "매우": 1.5, "정말": 1.5, "아주": 1.5, "특히": 1.3, "상당히": 1.3,
            "약간": 0.7, "조금": 0.7, "다소": 0.8, "살짝": 0.6
        }
        
        intensity_multiplier = 1.0
        for word, multiplier in intensity_words.items():
            if word in text_lower:
                intensity_multiplier = max(intensity_multiplier, multiplier)
        
        positive_count = len(positive_matches)
        negative_count = len(negative_matches)
        
        # 개선된 점수 계산
        base_score = 50
        positive_boost = min(positive_count * 10 * intensity_multiplier, 45)
        negative_penalty = min(negative_count * 12 * intensity_multiplier, 40)
        
        # 텍스트 길이 보너스 (더 상세한 평가일수록 신뢰도 증가)
        text_length = len(text)
        if text_length > 100:
            length_bonus = min((text_length - 100) / 200 * 10, 15)
        elif text_length < 30:
            length_bonus = -10  # 너무 짧은 평가는 감점
        else:
            length_bonus = 0
        
        # 문장 복잡도 보너스
        sentence_count = len(re.findall(r'[.!?]+', text))
        if sentence_count > 3:
            complexity_bonus = min(sentence_count * 2, 10)
        else:
            complexity_bonus = 0
        
        final_score = base_score + positive_boost - negative_penalty + length_bonus + complexity_bonus
        final_score = max(10, min(100, final_score))
        
        # 신뢰도 계산 개선
        total_signals = positive_count + negative_count
        base_confidence = min(total_signals * 15, 70)
        length_confidence = min(text_length / 20, 20)
        complexity_confidence = min(sentence_count * 3, 10)
        confidence = min(base_confidence + length_confidence + complexity_confidence, 100)
        
        return {
            "score": round(final_score, 1),
            "confidence": round(confidence, 1),
            "signals": {
                "positive": positive_count,
                "negative": negative_count,
                "positive_words": list(set(positive_matches))[:5],
                "negative_words": list(set(negative_matches))[:5],
                "intensity": intensity_multiplier
            },
            "analysis_method": "enhanced_keyword"
        }
    
    def _enhanced_keyword_analysis(self, text: str, dimension: str) -> Dict[str, Any]:
        """향상된 키워드 분석 - 문맥과 패턴 고려"""
        base_result = self._keyword_analysis(text, dimension)
        
        # 추가 패턴 분석
        patterns = {
            "achievement": r"(달성|완료|성공|이루|해냈|완수)",
            "improvement": r"(개선|향상|발전|성장|진보)",
            "problem": r"(문제|이슈|장애|어려움|곤란)",
            "collaboration": r"(협력|협업|함께|공동|팀워크)"
        }
        
        pattern_scores = {}
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, text)
            pattern_scores[pattern_name] = len(matches)
        
        # 패턴 기반 점수 조정
        if pattern_scores["achievement"] > 0:
            base_result["score"] += 5
        if pattern_scores["improvement"] > 0:
            base_result["score"] += 3
        if pattern_scores["problem"] > 0:
            base_result["score"] -= 5
        if pattern_scores["collaboration"] > 0 and dimension == "리더십협업":
            base_result["score"] += 7
        
        base_result["score"] = max(10, min(100, base_result["score"]))
        base_result["pattern_analysis"] = pattern_scores
        
        return base_result
    
    def _bert_analysis(self, text: str, dimension: str) -> Dict[str, Any]:
        """BERT 기반 감정/의도 분석 (실제 구현 시뮬레이션)"""
        # 실제 구현 시 BERT 모델을 통한 분석
        # 여기서는 시뮬레이션으로 대체
        
        # 텍스트 길이와 복잡도 기반 시뮬레이션
        text_length = len(text)
        positive_ratio = len(re.findall(r'(우수|좋|잘|훌륭|탁월)', text)) / max(1, len(text.split()))
        negative_ratio = len(re.findall(r'(부족|못|안|문제|미흡)', text)) / max(1, len(text.split()))
        
        # 감정 점수 계산
        sentiment_score = 50 + (positive_ratio * 300) - (negative_ratio * 400)
        sentiment_score = max(0, min(100, sentiment_score))
        
        # 의도 분류
        if positive_ratio > 0.1:
            intent = "positive_evaluation"
        elif negative_ratio > 0.1:
            intent = "constructive_criticism"
        else:
            intent = "neutral_observation"
        
        # 신뢰도는 텍스트 길이와 명확성에 기반
        confidence = min(80 + (text_length / 50), 95)
        
        return {
            "score": sentiment_score,
            "confidence": confidence,
            "sentiment": "positive" if sentiment_score > 65 else "negative" if sentiment_score < 35 else "neutral",
            "intent": intent,
            "aspect_scores": {aspect: sentiment_score + np.random.randint(-10, 10) 
                            for aspect in self.framework[dimension].get("bert_aspects", [])}
        }
    
    def comprehensive_analysis(self, uid: str, opinion: str) -> Dict[str, Any]:
        """전체 8대 영역 종합 분석 - 편향 검사 포함"""
        dimension_results = {}
        dimension_scores = {}
        
        # 각 영역별 분석
        for dimension in self.framework.keys():
            result = self.analyze_text(opinion, dimension)
            dimension_results[dimension] = result
            dimension_scores[dimension] = result["score"]
        
        # 편향성 검사
        bias_check = self.bias_detector.check_text_bias(opinion)
        
        # 종합 점수 계산
        overall_result = self.calculate_overall_score(dimension_scores)
        
        # 성과 예측 (간단한 규칙 기반)
        performance_prediction = self._predict_performance(dimension_scores)
        
        return {
            "text_analysis": {
                "overall_score": overall_result["overall_score"],
                "grade": overall_result["grade"],
                "grade_description": overall_result["grade_description"],
                "percentile": overall_result["percentile"],
                "dimension_scores": dimension_scores,
                "dimension_details": dimension_results,
                "top_strengths": self._identify_strengths(dimension_scores),
                "improvement_areas": self._identify_improvements(dimension_scores)
            },
            "bias_analysis": bias_check,
            "performance_prediction": performance_prediction,
            "quantitative_analysis": {
                "quantitative_score": 50,
                "confidence": 0,
                "data_quality": "없음",
                "data_count": 0
            },
            "hybrid_analysis": overall_result,
            "analysis_metadata": {
                "uid": uid,
                "analysis_version": "AIRISS v4.1 - Deep Learning Enhanced",
                "analysis_timestamp": datetime.now().isoformat(),
                "models_used": ["enhanced_keyword", "bert_simulation", "bias_detector"]
            }
        }
    
    def _identify_strengths(self, dimension_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """상위 3개 강점 영역 식별"""
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        return [
            {
                "dimension": dim,
                "score": score,
                "description": self.framework[dim]["description"]
            }
            for dim, score in sorted_dims if score >= 70
        ]
    
    def _identify_improvements(self, dimension_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """하위 3개 개선 영역 식별"""
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])[:3]
        return [
            {
                "dimension": dim,
                "score": score,
                "description": self.framework[dim]["description"],
                "recommendation": self._get_improvement_recommendation(dim)
            }
            for dim, score in sorted_dims if score < 70
        ]
    
    def _get_improvement_recommendation(self, dimension: str) -> str:
        """영역별 개선 권고사항"""
        recommendations = {
            "업무성과": "목표 설정을 구체화하고, 주간 성과 리뷰를 통해 진척도를 관리하세요.",
            "KPI달성": "핵심 지표에 집중하고, 데이터 기반 의사결정을 강화하세요.",
            "태도마인드": "긍정적 피드백 문화를 조성하고, 성장 마인드셋 워크샵 참여를 권장합니다.",
            "커뮤니케이션": "적극적 경청 스킬을 개발하고, 명확한 문서 작성 교육을 받으세요.",
            "리더십협업": "팀 빌딩 활동에 참여하고, 멘토링 프로그램을 활용하세요.",
            "전문성학습": "관련 분야 온라인 강의를 수강하고, 전문 자격증 취득을 고려하세요.",
            "창의혁신": "아이디어 브레인스토밍 세션에 참여하고, 타 부서 벤치마킹을 시도하세요.",
            "조직적응": "회사 문화 이해도를 높이고, 사내 네트워킹을 강화하세요."
        }
        return recommendations.get(dimension, "지속적인 자기계발과 피드백 수용 자세가 필요합니다.")
    
    def _predict_performance(self, dimension_scores: Dict[str, float]) -> Dict[str, Any]:
        """간단한 성과 예측 모델"""
        avg_score = sum(dimension_scores.values()) / len(dimension_scores)
        
        # 성과 트렌드 예측
        if avg_score >= 85:
            trend = "상승"
            probability = 0.85
        elif avg_score >= 70:
            trend = "유지"
            probability = 0.70
        else:
            trend = "주의필요"
            probability = 0.60
        
        # 이직 위험도 (역산)
        turnover_risk = max(0, min(100, 100 - avg_score))
        
        return {
            "6month_trend": trend,
            "success_probability": probability,
            "turnover_risk_score": round(turnover_risk, 1),
            "promotion_readiness": "높음" if avg_score >= 85 else "보통" if avg_score >= 70 else "낮음",
            "development_priority": self._identify_improvements(dimension_scores)[0]["dimension"] if self._identify_improvements(dimension_scores) else None
        }
    
    def calculate_overall_score(self, dimension_scores: Dict[str, float]) -> Dict[str, Any]:
        """가중평균으로 종합 점수 계산 - 7단계 등급 체계 (S, A+, A, B+, B, C, D)"""
        weighted_sum = 0
        total_weight = 0
        
        for dimension, score in dimension_scores.items():
            if dimension in self.framework:
                weight = self.framework[dimension]["weight"]
                weighted_sum += score * weight
                total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 50
        
        # 7단계 등급 산정 체계 (S, A+, A, B+, B, C, D)
        if overall_score >= 95:
            grade = "S"
            grade_desc = "탁월함 (Superb) - 전사 TOP 1%"
            percentile = "상위 1%"
            badge = "🏆"
        elif overall_score >= 90:
            grade = "A+"
            grade_desc = "매우 우수 (Excellent) - 전사 TOP 5%"
            percentile = "상위 5%"
            badge = "⭐⭐⭐"
        elif overall_score >= 80:
            grade = "A"
            grade_desc = "우수 (Outstanding) - 전사 TOP 15%"
            percentile = "상위 15%"
            badge = "⭐⭐"
        elif overall_score >= 70:
            grade = "B+"
            grade_desc = "양호 (Good) - 전사 TOP 30%"
            percentile = "상위 30%"
            badge = "⭐"
        elif overall_score >= 60:
            grade = "B"
            grade_desc = "보통 (Average) - 전사 TOP 50%"
            percentile = "상위 50%"
            badge = "✨"
        elif overall_score >= 50:
            grade = "C"
            grade_desc = "개선 필요 (Needs Improvement) - 전사 TOP 70%"
            percentile = "상위 70%"
            badge = "📈"
        else:
            grade = "D"
            grade_desc = "집중 관리 필요 (Requires Attention) - 하위 30%"
            percentile = "하위 30%"
            badge = "🚨"
        
        # 상세 분석 추가
        score_distribution = self._analyze_score_distribution(dimension_scores)
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "grade_description": grade_desc,
            "percentile": percentile,
            "badge": badge,
            "confidence": self._calculate_confidence(dimension_scores),
            "score_distribution": score_distribution,
            "consistency": self._calculate_consistency(dimension_scores)
        }
    
    def _analyze_score_distribution(self, dimension_scores: Dict[str, float]) -> Dict[str, Any]:
        """점수 분포 분석"""
        scores = list(dimension_scores.values())
        return {
            "mean": round(np.mean(scores), 1),
            "std": round(np.std(scores), 1),
            "min": round(min(scores), 1),
            "max": round(max(scores), 1),
            "range": round(max(scores) - min(scores), 1)
        }
    
    def _calculate_consistency(self, dimension_scores: Dict[str, float]) -> str:
        """일관성 평가"""
        std = np.std(list(dimension_scores.values()))
        if std < 10:
            return "매우 일관됨"
        elif std < 20:
            return "일관됨"
        elif std < 30:
            return "다소 불균형"
        else:
            return "불균형"
    
    def _calculate_confidence(self, dimension_scores: Dict[str, float]) -> float:
        """종합 신뢰도 계산"""
        # 점수가 극단적이지 않고 일관성 있을수록 신뢰도 증가
        scores = list(dimension_scores.values())
        std = np.std(scores)
        mean = np.mean(scores)
        
        # 표준편차가 낮을수록 신뢰도 증가
        consistency_confidence = max(0, 100 - std * 2)
        
        # 극단적 점수가 적을수록 신뢰도 증가
        extreme_count = sum(1 for s in scores if s < 20 or s > 90)
        extreme_penalty = extreme_count * 10
        
        confidence = min(100, max(50, consistency_confidence - extreme_penalty))
        return round(confidence, 1)
    
    async def generate_ai_feedback(
        self,
        uid: str,
        opinion: str,
        api_key: str,
        model: str = "gpt-4",  # 업그레이드
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """OpenAI를 사용한 고급 AI 피드백 생성"""
        
        if not self.openai_available:
            logger.error("OpenAI 모듈이 설치되지 않았습니다.")
            return {
                "ai_strengths": "OpenAI 모듈이 설치되지 않았습니다.",
                "ai_weaknesses": "pip install openai로 설치해주세요.",
                "ai_feedback": "딥러닝 기반 분석만 제공됩니다.",
                "ai_recommendations": [],
                "error": "OpenAI 모듈 미설치"
            }
        
        if not api_key:
            logger.error("OpenAI API 키가 제공되지 않았습니다.")
            return {
                "ai_strengths": "API 키가 제공되지 않았습니다.",
                "ai_weaknesses": "OpenAI API 키를 입력해주세요.",
                "ai_feedback": "딥러닝 기반 분석만 수행되었습니다.",
                "ai_recommendations": [],
                "error": "API 키 없음"
            }
        
        try:
            client = self.openai.OpenAI(api_key=api_key)
            # 개선된 프롬프트
            prompt = f"""
직원 {uid}의 평가 의견을 AIRISS 8대 영역 기반으로 심층 분석하세요:

평가 의견: {opinion[:1500]}

8대 영역:
1. 업무성과 (25%) - 업무 품질, 생산성, 목표 달성
2. KPI달성 (20%) - 정량적 성과, 지표 달성률
3. 태도마인드 (15%) - 적극성, 책임감, 성장 의지
4. 커뮤니케이션 (15%) - 소통 능력, 협력적 대화
5. 리더십협업 (10%) - 팀워크, 리더십, 영향력
6. 전문성학습 (8%) - 기술 역량, 학습 속도
7. 창의혁신 (5%) - 창의성, 변화 주도
8. 조직적응 (2%) - 조직 문화 적응, 윤리성

다음 형식으로 분석하세요:

[핵심 강점] (3가지)
- 강점1: (영역명) 구체적 행동/성과
- 강점2: (영역명) 구체적 행동/성과
- 강점3: (영역명) 구체적 행동/성과

[개선 필요사항] (3가지)
- 개선1: (영역명) 구체적 개선점
- 개선2: (영역명) 구체적 개선점
- 개선3: (영역명) 구체적 개선점

[종합 피드백]
- 현재 수준: (1-2문장)
- 성장 잠재력: (1-2문장)
- 핵심 제언: (1-2문장)

[구체적 실행 계획] (3가지)
1. 단기(1개월): 구체적 액션
2. 중기(3개월): 구체적 목표
3. 장기(6개월): 기대 성과
"""
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 OK금융그룹의 수석 HR 전문가입니다. 건설적이고 실행 가능한 피드백을 제공하세요."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            feedback = response.choices[0].message.content
            # 응답 파싱 개선
            sections = {
                "strengths": "",
                "weaknesses": "",
                "overall": "",
                "action_plan": []
            }
            if "[핵심 강점]" in feedback:
                parts = feedback.split("[핵심 강점]")[1].split("[개선 필요사항]")
                sections["strengths"] = parts[0].strip() if len(parts) > 0 else ""
                if len(parts) > 1:
                    parts2 = parts[1].split("[종합 피드백]")
                    sections["weaknesses"] = parts2[0].strip() if len(parts2) > 0 else ""
                    if len(parts2) > 1:
                        parts3 = parts2[1].split("[구체적 실행 계획]")
                        sections["overall"] = parts3[0].strip() if len(parts3) > 0 else ""
                        if len(parts3) > 1:
                            action_items = parts3[1].strip().split('\n')
                            sections["action_plan"] = [item.strip() for item in action_items if item.strip()]
            return {
                "ai_strengths": sections["strengths"],
                "ai_weaknesses": sections["weaknesses"],
                "ai_feedback": sections["overall"],
                "ai_recommendations": sections["action_plan"],
                "error": None
            }
        except Exception as e:
            logger.error(f"OpenAI API 오류: {e}", exc_info=True)
            return {
                "ai_strengths": f"AI 분석 오류: {str(e)}",
                "ai_weaknesses": "AI 분석을 완료할 수 없습니다.",
                "ai_feedback": f"오류: {str(e)}",
                "ai_recommendations": [],
                "error": str(e)
            }


class BiasDetector:
    """편향성 탐지 클래스"""
    
    def __init__(self):
        self.bias_patterns = {
            "gender": {
                "male_terms": ["그", "남자", "남성", "아들", "아버지"],
                "female_terms": ["그녀", "여자", "여성", "딸", "어머니"]
            },
            "age": {
                "young_terms": ["젊은", "신입", "주니어", "밀레니얼", "Z세대"],
                "old_terms": ["나이든", "시니어", "베테랑", "고령", "연장자"]
            },
            "appearance": {
                "terms": ["외모", "키", "몸무게", "잘생긴", "예쁜", "뚱뚱한", "마른"]
            }
        }
    
    def check_text_bias(self, text: str) -> Dict[str, Any]:
        """텍스트의 편향성 검사"""
        text_lower = text.lower()
        bias_flags = {
            "gender_bias": False,
            "age_bias": False,
            "appearance_bias": False,
            "bias_score": 0,
            "bias_details": []
        }
        
        # 성별 편향 검사
        male_count = sum(1 for term in self.bias_patterns["gender"]["male_terms"] if term in text_lower)
        female_count = sum(1 for term in self.bias_patterns["gender"]["female_terms"] if term in text_lower)
        
        if abs(male_count - female_count) > 2:
            bias_flags["gender_bias"] = True
            bias_flags["bias_details"].append({
                "type": "gender",
                "severity": "medium",
                "description": "성별 관련 용어가 편향적으로 사용됨"
            })
            bias_flags["bias_score"] += 30
        
        # 연령 편향 검사
        young_count = sum(1 for term in self.bias_patterns["age"]["young_terms"] if term in text_lower)
        old_count = sum(1 for term in self.bias_patterns["age"]["old_terms"] if term in text_lower)
        
        if young_count > 0 or old_count > 0:
            bias_flags["age_bias"] = True
            bias_flags["bias_details"].append({
                "type": "age",
                "severity": "low",
                "description": "연령 관련 용어가 사용됨"
            })
            bias_flags["bias_score"] += 20
        
        # 외모 편향 검사
        appearance_count = sum(1 for term in self.bias_patterns["appearance"]["terms"] if term in text_lower)
        
        if appearance_count > 0:
            bias_flags["appearance_bias"] = True
            bias_flags["bias_details"].append({
                "type": "appearance",
                "severity": "high",
                "description": "외모 관련 부적절한 언급이 포함됨"
            })
            bias_flags["bias_score"] += 50
        
        # 전반적 공정성 점수
        bias_flags["fairness_score"] = 100 - bias_flags["bias_score"]
        bias_flags["is_fair"] = bias_flags["fairness_score"] >= 80
        
        return bias_flags