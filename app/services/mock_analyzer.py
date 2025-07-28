"""
Mock Analyzer for Railway deployment
Provides basic analysis when AI dependencies are not available
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)

class MockTextAnalyzer:
    """간단한 텍스트 분석기 (AI 없이)"""
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """텍스트 기본 분석"""
        if not text:
            return {
                "length": 0,
                "word_count": 0,
                "sentiment": "neutral",
                "confidence": 0.5
            }
        
        words = text.split()
        
        # 간단한 감정 분석 (키워드 기반)
        positive_words = ["좋음", "우수", "훌륭", "뛰어남", "만족", "good", "excellent", "great"]
        negative_words = ["나쁨", "부족", "미흡", "개선", "bad", "poor", "needs improvement"]
        
        positive_count = sum(1 for word in words if any(p in word.lower() for p in positive_words))
        negative_count = sum(1 for word in words if any(n in word.lower() for n in negative_words))
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "length": len(text),
            "word_count": len(words),
            "sentiment": sentiment,
            "confidence": 0.7,
            "positive_score": positive_count / max(len(words), 1),
            "negative_score": negative_count / max(len(words), 1)
        }
    
    async def generate_ai_feedback(self, employee_data: Dict[str, Any]) -> Dict[str, str]:
        """AI 피드백 생성 (모의)"""
        
        # 기본 피드백 템플릿
        templates = {
            "high_performer": {
                "ai_strengths": "우수한 성과를 보이고 있으며, 팀에 긍정적인 영향을 미치고 있습니다.",
                "ai_weaknesses": "지속적인 성장을 위해 새로운 도전 과제가 필요할 수 있습니다.",
                "ai_recommendations": "리더십 역할 확대 및 멘토링 기회 제공을 고려해보세요.",
                "ai_feedback": "전반적으로 뛰어난 성과를 보이고 있습니다."
            },
            "average_performer": {
                "ai_strengths": "안정적인 업무 수행 능력을 보여주고 있습니다.",
                "ai_weaknesses": "일부 영역에서 개선의 여지가 있습니다.",
                "ai_recommendations": "추가 교육 및 스킬 개발 프로그램 참여를 권장합니다.",
                "ai_feedback": "꾸준한 성과를 보이고 있으며, 발전 가능성이 있습니다."
            },
            "low_performer": {
                "ai_strengths": "기본적인 업무는 수행하고 있습니다.",
                "ai_weaknesses": "여러 영역에서 개선이 필요합니다.",
                "ai_recommendations": "집중적인 코칭과 명확한 목표 설정이 필요합니다.",
                "ai_feedback": "성과 개선을 위한 적극적인 지원이 필요합니다."
            }
        }
        
        # 점수 기반 카테고리 결정
        score = employee_data.get("종합점수", 50)
        if score >= 80:
            category = "high_performer"
        elif score >= 60:
            category = "average_performer"
        else:
            category = "low_performer"
        
        return templates[category]

class MockQuantitativeAnalyzer:
    """간단한 정량 분석기"""
    
    def analyze_scores(self, scores: List[float]) -> Dict[str, Any]:
        """점수 통계 분석"""
        if not scores:
            return {
                "mean": 0,
                "std": 0,
                "min": 0,
                "max": 0,
                "percentile_25": 0,
                "percentile_50": 0,
                "percentile_75": 0
            }
        
        scores_array = np.array(scores)
        
        return {
            "mean": float(np.mean(scores_array)),
            "std": float(np.std(scores_array)),
            "min": float(np.min(scores_array)),
            "max": float(np.max(scores_array)),
            "percentile_25": float(np.percentile(scores_array, 25)),
            "percentile_50": float(np.percentile(scores_array, 50)),
            "percentile_75": float(np.percentile(scores_array, 75))
        }
    
    def categorize_performance(self, score: float) -> str:
        """성과 카테고리 분류"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"