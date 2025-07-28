"""
AI Service
OpenAI API를 사용한 AI 분석 서비스
"""

from typing import Dict, Any, List, Optional
import openai
import json
import asyncio
from datetime import datetime
import logging

from app.core.config import settings


class AIService:
    """AI 분석 서비스"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.api_key = settings.OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key
    
    async def generate_feedback(
        self,
        opinion: str,
        score: float,
        model: str = None,
        max_tokens: int = None
    ) -> Dict[str, Any]:
        """AI 피드백 생성"""
        if not self.api_key:
            self.logger.warning("OpenAI API key not configured")
            return {}
        
        try:
            # 프롬프트 구성
            prompt = self._create_feedback_prompt(opinion, score)
            
            # API 호출
            response = await self._call_openai(
                prompt,
                model or settings.DEFAULT_AI_MODEL,
                max_tokens or settings.DEFAULT_MAX_TOKENS
            )
            
            # 응답 파싱
            feedback = self._parse_ai_response(response)
            
            return {
                'ai_feedback': feedback,
                'ai_strengths': feedback.get('strengths', ''),
                'ai_weaknesses': feedback.get('weaknesses', ''),
                'ai_recommendations': feedback.get('recommendations', [])
            }
            
        except Exception as e:
            self.logger.error(f"AI feedback generation failed: {e}")
            return {
                'ai_error': str(e)
            }
    
    def _create_feedback_prompt(self, opinion: str, score: float) -> str:
        """피드백 생성용 프롬프트 생성"""
        return f"""
직원의 의견/피드백을 분석하고 구조화된 평가를 제공해주세요.

직원 의견: {opinion}
현재 점수: {score}/100

다음 형식의 JSON으로 응답해주세요:
{{
    "strengths": "주요 강점 (2-3문장)",
    "weaknesses": "개선이 필요한 부분 (2-3문장)",
    "recommendations": ["구체적인 개선 제안 1", "구체적인 개선 제안 2", "구체적인 개선 제안 3"],
    "leadership_score": 0-100,
    "communication_score": 0-100,
    "problem_solving_score": 0-100,
    "teamwork_score": 0-100,
    "innovation_score": 0-100,
    "execution_score": 0-100
}}
"""
    
    async def _call_openai(self, prompt: str, model: str, max_tokens: int) -> str:
        """OpenAI API 호출"""
        # 비동기 처리를 위한 래퍼
        loop = asyncio.get_event_loop()
        
        def sync_call():
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an HR analytics expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message['content']
        
        # 동기 함수를 비동기로 실행
        response = await loop.run_in_executor(None, sync_call)
        return response
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """AI 응답 파싱"""
        try:
            # JSON 파싱 시도
            return json.loads(response)
        except json.JSONDecodeError:
            # JSON 파싱 실패시 텍스트로 처리
            return {
                'overall_assessment': response,
                'strengths': '',
                'weaknesses': '',
                'recommendations': []
            }
    
    async def batch_analyze(
        self,
        opinions: List[str],
        model: str = None,
        max_tokens: int = None
    ) -> List[Dict[str, Any]]:
        """배치 분석"""
        tasks = []
        for opinion in opinions:
            task = self.generate_feedback(opinion, 70, model, max_tokens)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 오류 처리
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Batch analysis failed for item {i}: {result}")
                processed_results.append({'ai_error': str(result)})
            else:
                processed_results.append(result)
        
        return processed_results
    
    def validate_api_key(self) -> bool:
        """API 키 유효성 검증"""
        if not self.api_key:
            return False
        
        try:
            # 간단한 API 호출로 검증
            openai.Model.list()
            return True
        except Exception as e:
            self.logger.error(f"API key validation failed: {e}")
            return False