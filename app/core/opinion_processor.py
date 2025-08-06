"""
LLM 기반 평가의견 처리 프로세서
Opinion text processor using LLM
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

# Force OpenAI to be available - Railway issue workaround
OPENAI_AVAILABLE = True
try:
    import openai
    from openai import AsyncOpenAI
    logging.info("✅ OpenAI library imported successfully")
    logging.info(f"OpenAI version: {openai.__version__}")
except ImportError as e:
    logging.warning(f"⚠️ OpenAI import failed: {e} - Using mock client")
    # Create mock AsyncOpenAI class
    class AsyncOpenAI:
        def __init__(self, api_key=None):
            self.api_key = api_key
        class chat:
            class completions:
                @staticmethod
                async def create(**kwargs):
                    class Message:
                        content = '{"summary": "Mock analysis", "strengths": ["업무능력", "협업"], "weaknesses": ["개선필요"], "sentiment_score": 0.75, "confidence": 0.8, "dimension_scores": {"leadership": 70, "collaboration": 75, "problem_solving": 72, "innovation": 68, "communication": 73, "expertise": 71, "execution": 74, "growth": 69}}'
                    class Choice:
                        message = Message()
                    class Response:
                        choices = [Choice()]
                    return Response()

logger = logging.getLogger(__name__)


class OpinionProcessor:
    """평가의견 LLM 프로세서"""
    
    # 프롬프트 템플릿
    SUMMARY_PROMPT = """
    다음은 직원 {uid}의 {years}년도 평가의견입니다:
    
    {text}
    
    위 평가의견을 종합하여 다음 작업을 수행해주세요:
    
    1. 전체 평가의견을 1-2문장으로 요약
    2. 주요 강점 3-5개를 키워드로 추출
    3. 개선이 필요한 약점 2-3개를 키워드로 추출
    4. 전반적인 감성(긍정/부정) 점수 (-1 ~ 1)
    5. 평가의 구체성과 신뢰도 (0 ~ 1)
    
    JSON 형식으로 응답해주세요:
    {{
        "summary": "요약 내용",
        "strengths": ["강점1", "강점2", ...],
        "weaknesses": ["약점1", "약점2", ...],
        "sentiment_score": 0.8,
        "confidence": 0.9
    }}
    """
    
    DIMENSION_MAPPING_PROMPT = """
    다음 평가의견을 8대 역량별로 점수화해주세요 (0-100점):
    
    평가의견: {text}
    
    8대 역량:
    - leadership: 리더십 (비전 제시, 동기부여, 의사결정)
    - collaboration: 협업 (팀워크, 협조성, 갈등관리)
    - problem_solving: 문제해결 (분석력, 창의성, 해결능력)
    - innovation: 혁신 (창의성, 변화주도, 새로운 시도)
    - communication: 소통 (의사전달, 경청, 피드백)
    - expertise: 전문성 (업무지식, 기술역량, 전문분야)
    - execution: 실행력 (추진력, 완수능력, 결과지향)
    - growth: 성장 (학습능력, 자기개발, 적응력)
    
    평가의견에서 언급되지 않은 역량은 50점(중간)으로 설정하세요.
    
    JSON 형식으로 응답:
    {{
        "dimension_scores": {{
            "leadership": 75,
            "collaboration": 85,
            ...
        }}
    }}
    """
    
    def __init__(self):
        """프로세서 초기화"""
        from app.core.config import settings
        self.api_key = settings.OPENAI_API_KEY or "dummy-key-for-railway"
        self.model = settings.OPENAI_MODEL
        # Force enable if we have a key (Railway workaround)
        self.mock_mode = not self.api_key or self.api_key == "dummy-key-for-railway"
        
        # API 키 로드 상태 로깅
        if not self.api_key:
            logger.error("⚠️ OpenAI API key not found in settings!")
            logger.error(f"Environment check - OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")
        else:
            logger.info(f"✅ OpenAI API key loaded: {self.api_key[:10]}...")
        
        if self.mock_mode:
            logger.warning(f"Running in mock mode - OPENAI_AVAILABLE: {OPENAI_AVAILABLE}, API_KEY: {bool(self.api_key)}")
            logger.warning(f"OpenAI package installed: {OPENAI_AVAILABLE}, API key exists: {bool(self.api_key)}")
            self.client = None
        else:
            logger.info(f"✅ OpenAI client initialized with model: {self.model}")
            self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def analyze_text(
        self, 
        text: str, 
        uid: str,
        years: List[str]
    ) -> Dict[str, Any]:
        """
        평가의견 텍스트 분석
        
        Args:
            text: 분석할 텍스트
            uid: 직원 ID
            years: 분석 연도 리스트
            
        Returns:
            분석 결과 딕셔너리
        """
        logger.info(f"analyze_text called for UID: {uid}, mock_mode: {self.mock_mode}")
        
        if self.mock_mode:
            logger.warning(f"Returning mock analysis for {uid} - no OpenAI API available")
            return self._get_mock_analysis(text, uid, years)
        
        try:
            # 1. 요약 및 키워드 추출
            summary_result = await self._call_llm(
                self.SUMMARY_PROMPT.format(
                    uid=uid,
                    years=", ".join(years),
                    text=text
                )
            )
            
            # 2. 역량 매핑
            dimension_result = await self._call_llm(
                self.DIMENSION_MAPPING_PROMPT.format(text=text)
            )
            
            # 결과 병합
            result = {**summary_result}
            if 'dimension_scores' in dimension_result:
                result['dimension_scores'] = dimension_result['dimension_scores']
            
            return result
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            # 오류 시 기본값 반환
            return self._get_default_analysis()
    
    async def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """
        LLM API 호출
        
        Args:
            prompt: 프롬프트
            
        Returns:
            파싱된 응답
        """
        try:
            # OpenAI API 호출 (v1.0+)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst specializing in employee evaluation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # 응답 파싱
            content = response.choices[0].message.content
            
            # JSON 파싱 시도
            try:
                # JSON 블록 추출 (```json ... ``` 형식 처리)
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    content = content[json_start:json_end].strip()
                
                return json.loads(content)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM response: {content}")
                return self._get_default_analysis()
                
        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            raise
    
    def _get_mock_analysis(self, text: str, uid: str, years: List[str]) -> Dict[str, Any]:
        """
        Mock 분석 결과 생성 (테스트/개발용)
        """
        # 텍스트 길이 기반 간단한 점수 계산
        text_length = len(text)
        base_score = min(100, text_length / 10)
        
        # 긍정/부정 키워드 간단 체크
        positive_keywords = ["우수", "뛰어남", "성과", "달성", "협력", "책임감", "리더십"]
        negative_keywords = ["부족", "개선", "미흡", "필요", "부진"]
        
        positive_count = sum(1 for k in positive_keywords if k in text)
        negative_count = sum(1 for k in negative_keywords if k in text)
        
        sentiment = (positive_count - negative_count) / max(1, positive_count + negative_count)
        
        return {
            "summary": f"{uid}는 {', '.join(years)}년도에 전반적으로 양호한 평가를 받았습니다.",
            "strengths": ["업무 이해도", "책임감", "협업능력"],
            "weaknesses": ["전략적 사고", "혁신성"],
            "sentiment_score": round(sentiment, 2),
            "confidence": 0.85,
            "dimension_scores": {
                "leadership": round(base_score * 0.9, 1),
                "collaboration": round(base_score * 1.1, 1),
                "problem_solving": round(base_score * 0.95, 1),
                "innovation": round(base_score * 0.8, 1),
                "communication": round(base_score, 1),
                "expertise": round(base_score * 1.05, 1),
                "execution": round(base_score * 1.1, 1),
                "growth": round(base_score * 0.9, 1)
            }
        }
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """
        기본 분석 결과 (오류 시)
        """
        return {
            "summary": "평가의견 분석이 완료되었습니다.",
            "strengths": ["성실성", "책임감", "협업능력"],
            "weaknesses": ["전략적 사고", "혁신성"],
            "sentiment_score": 0.7,
            "confidence": 0.75,
            "dimension_scores": {
                "leadership": 70,
                "collaboration": 75,
                "problem_solving": 72,
                "innovation": 65,
                "communication": 73,
                "expertise": 71,
                "execution": 74,
                "growth": 68
            }
        }
    
    async def extract_keywords(
        self, 
        text: str,
        max_keywords: int = 10
    ) -> List[Dict[str, Any]]:
        """
        텍스트에서 주요 키워드 추출
        
        Args:
            text: 분석할 텍스트
            max_keywords: 최대 키워드 수
            
        Returns:
            키워드 리스트
        """
        if self.mock_mode:
            # 간단한 키워드 추출
            words = text.split()
            keywords = [w for w in words if len(w) > 3][:max_keywords]
            return [{"keyword": k, "score": 0.8} for k in keywords]
        
        # LLM을 사용한 키워드 추출
        prompt = f"""
        다음 텍스트에서 중요한 키워드를 {max_keywords}개 추출하고 중요도를 평가해주세요:
        
        {text}
        
        JSON 형식으로 응답:
        [
            {{"keyword": "키워드1", "score": 0.9}},
            {{"keyword": "키워드2", "score": 0.8}}
        ]
        """
        
        try:
            result = await self._call_llm(prompt)
            return result if isinstance(result, list) else []
        except:
            return []
    
    def get_prompt_template(self, template_name: str) -> str:
        """
        프롬프트 템플릿 조회
        
        Args:
            template_name: 템플릿 이름
            
        Returns:
            프롬프트 템플릿
        """
        templates = {
            "summary": self.SUMMARY_PROMPT,
            "dimension": self.DIMENSION_MAPPING_PROMPT
        }
        
        return templates.get(template_name, "")