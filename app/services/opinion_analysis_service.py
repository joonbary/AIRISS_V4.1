"""
평가의견 분석 서비스
Opinion analysis service with LLM integration
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import uuid
import asyncio

from sqlalchemy.orm import Session

from app.models.opinion_result import OpinionResult, OpinionKeyword
from app.models.employee import EmployeeResult
from app.schemas.opinion import (
    OpinionUploadRequest, 
    OpinionAnalysisResult,
    DimensionScore,
    HybridScoreConfig
)
from app.utils.text_cleaning import TextCleaner, merge_yearly_opinions
from app.core.opinion_processor import OpinionProcessor
from app.db.repositories.opinion_repository import OpinionRepository

logger = logging.getLogger(__name__)


class OpinionAnalysisService:
    """평가의견 분석 서비스"""
    
    # 8대 역량 정의
    DIMENSIONS = [
        "leadership",      # 리더십
        "collaboration",   # 협업
        "problem_solving", # 문제해결
        "innovation",      # 혁신
        "communication",   # 소통
        "expertise",       # 전문성
        "execution",       # 실행력
        "growth"          # 성장
    ]
    
    def __init__(self, db: Session):
        """
        서비스 초기화
        
        Args:
            db: 데이터베이스 세션
        """
        self.db = db
        self.text_cleaner = TextCleaner()
        self.opinion_processor = OpinionProcessor()
        self.opinion_repo = OpinionRepository(db)
        
    async def analyze_opinion(
        self, 
        request: OpinionUploadRequest,
        hybrid_config: Optional[HybridScoreConfig] = None
    ) -> OpinionAnalysisResult:
        """
        평가의견 분석 메인 함수
        
        Args:
            request: 평가의견 업로드 요청
            hybrid_config: 하이브리드 점수 계산 설정
            
        Returns:
            분석 결과
        """
        start_time = datetime.now()
        
        try:
            # 1. 텍스트 정제 및 전처리
            cleaned_opinions = self._preprocess_opinions(request.opinions)
            if not cleaned_opinions:
                raise ValueError(f"No valid opinions found for UID: {request.uid}")
            
            # 2. 연도별 의견 병합
            merged_text = merge_yearly_opinions(cleaned_opinions)
            years_analyzed = list(cleaned_opinions.keys())
            
            # 3. LLM 분석 실행
            llm_result = await self.opinion_processor.analyze_text(
                text=merged_text,
                uid=request.uid,
                years=years_analyzed
            )
            
            # 4. 텍스트 점수 계산
            text_scores = self._calculate_text_scores(
                merged_text=merged_text,
                llm_result=llm_result,
                yearly_opinions=cleaned_opinions
            )
            
            # 5. 8대 역량 점수 계산
            dimension_scores = await self._calculate_dimension_scores(
                llm_result=llm_result,
                text=merged_text
            )
            
            # 6. 하이브리드 점수 계산
            hybrid_score = await self._calculate_hybrid_score(
                uid=request.uid,
                text_score=text_scores['text_score'],
                config=hybrid_config or HybridScoreConfig()
            )
            
            # 7. 결과 저장
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = await self._save_analysis_result(
                uid=request.uid,
                raw_opinions=request.opinions,
                cleaned_opinions=cleaned_opinions,
                llm_result=llm_result,
                text_scores=text_scores,
                dimension_scores=dimension_scores,
                hybrid_score=hybrid_score,
                processing_time=processing_time
            )
            
            logger.info(f"Opinion analysis completed for UID: {request.uid} in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Opinion analysis failed for UID {request.uid}: {str(e)}")
            raise
    
    def _preprocess_opinions(self, opinions: Dict[str, Optional[str]]) -> Dict[str, str]:
        """
        평가의견 전처리
        
        Args:
            opinions: 원본 평가의견 딕셔너리
            
        Returns:
            정제된 평가의견 딕셔너리
        """
        cleaned = {}
        
        for year, text in opinions.items():
            if text:
                cleaned_text = self.text_cleaner.clean(text)
                if cleaned_text:
                    cleaned[year] = cleaned_text
                    
        return self.text_cleaner.normalize_year_format(cleaned)
    
    def _calculate_text_scores(
        self, 
        merged_text: str,
        llm_result: dict,
        yearly_opinions: Dict[str, str]
    ) -> dict:
        """
        텍스트 기반 점수 계산
        
        Returns:
            dict with text_score, sentiment_score, specificity_score, consistency_score
        """
        # 감성 점수 (LLM 결과 활용)
        sentiment_score = llm_result.get('sentiment_score', 0.0)
        
        # 구체성 점수 계산
        specificity_score = self._calculate_specificity(merged_text)
        
        # 일관성 점수 계산 (연도별 의견 비교)
        consistency_score = self._calculate_consistency(yearly_opinions)
        
        # 종합 텍스트 점수 (0-100)
        text_score = (
            (sentiment_score + 1) * 25 +  # -1~1 -> 0~50
            specificity_score * 30 +       # 0~1 -> 0~30
            consistency_score * 20         # 0~1 -> 0~20
        )
        
        return {
            'text_score': min(100, max(0, text_score)),
            'sentiment_score': sentiment_score,
            'specificity_score': specificity_score,
            'consistency_score': consistency_score
        }
    
    def _calculate_specificity(self, text: str) -> float:
        """
        텍스트 구체성 점수 계산
        
        구체적인 행동, 성과, 숫자 등이 포함된 정도를 평가
        """
        specificity_indicators = [
            r'\d+[%％]',  # 퍼센트
            r'\d+[\s]*(개월|년|명|건|회)',  # 숫자 + 단위
            r'(달성|완료|개선|증가|감소|향상)',  # 성과 동사
            r'(프로젝트|과제|업무|목표)',  # 구체적 명사
            r'(KPI|ROI|매출|비용|효율)',  # 비즈니스 용어
        ]
        
        score = 0
        text_length = len(text)
        
        for pattern in specificity_indicators:
            import re
            matches = re.findall(pattern, text)
            score += len(matches) * 0.1
        
        # 문장 길이도 고려 (너무 짧으면 구체성 부족)
        if text_length > 100:
            score += 0.2
        if text_length > 200:
            score += 0.1
            
        return min(1.0, score)
    
    def _calculate_consistency(self, yearly_opinions: Dict[str, str]) -> float:
        """
        연도별 평가의견 일관성 계산
        
        여러 해에 걸쳐 비슷한 평가를 받았는지 확인
        """
        if len(yearly_opinions) <= 1:
            return 0.8  # 데이터가 적으면 중간 점수
        
        # 간단한 일관성 체크 (실제로는 더 정교한 알고리즘 필요)
        opinions_list = list(yearly_opinions.values())
        
        # 키워드 추출 및 비교
        common_keywords = set()
        all_keywords = []
        
        for opinion in opinions_list:
            # 간단한 키워드 추출 (명사, 형용사)
            words = opinion.split()
            keywords = [w for w in words if len(w) > 2]
            all_keywords.append(set(keywords))
        
        # 공통 키워드 비율 계산
        if all_keywords:
            common_keywords = all_keywords[0]
            for keywords in all_keywords[1:]:
                common_keywords = common_keywords.intersection(keywords)
            
            total_unique_keywords = set()
            for keywords in all_keywords:
                total_unique_keywords.update(keywords)
            
            if total_unique_keywords:
                consistency = len(common_keywords) / len(total_unique_keywords)
                return min(1.0, consistency * 2)  # 보정
        
        return 0.5
    
    async def _calculate_dimension_scores(
        self, 
        llm_result: dict,
        text: str
    ) -> DimensionScore:
        """
        8대 역량별 점수 계산
        """
        # LLM 결과에서 역량 점수 추출
        dimension_scores = llm_result.get('dimension_scores', {})
        
        # 기본값 설정
        scores = {}
        for dim in self.DIMENSIONS:
            scores[dim] = dimension_scores.get(dim, 50.0)  # 기본값 50
        
        return DimensionScore(**scores)
    
    async def _calculate_hybrid_score(
        self,
        uid: str,
        text_score: float,
        config: HybridScoreConfig
    ) -> float:
        """
        정량 점수와 텍스트 점수를 결합한 하이브리드 점수 계산
        """
        # 기존 정량 점수 조회
        employee_result = self.db.query(EmployeeResult).filter(
            EmployeeResult.uid == uid
        ).first()
        
        if not employee_result:
            # 정량 점수가 없으면 텍스트 점수만 반환
            return text_score
        
        quantitative_score = employee_result.overall_score or 50.0
        
        # 가중 평균 계산
        hybrid_score = (
            quantitative_score * config.quantitative_weight +
            text_score * config.text_weight
        )
        
        return round(hybrid_score, 2)
    
    async def _save_analysis_result(
        self,
        uid: str,
        raw_opinions: dict,
        cleaned_opinions: dict,
        llm_result: dict,
        text_scores: dict,
        dimension_scores: DimensionScore,
        hybrid_score: float,
        processing_time: float
    ) -> OpinionAnalysisResult:
        """
        분석 결과 데이터베이스 저장
        """
        # OpinionResult 생성
        result_id = str(uuid.uuid4())
        
        opinion_result = OpinionResult(
            id=result_id,
            uid=uid,
            raw_opinions=raw_opinions,
            years_analyzed=list(cleaned_opinions.keys()),
            summary=llm_result.get('summary', ''),
            strengths=llm_result.get('strengths', []),
            weaknesses=llm_result.get('weaknesses', []),
            text_score=text_scores['text_score'],
            sentiment_score=text_scores['sentiment_score'],
            specificity_score=text_scores['specificity_score'],
            consistency_score=text_scores['consistency_score'],
            dimension_scores=dimension_scores.dict(),
            hybrid_score=hybrid_score,
            confidence=llm_result.get('confidence', 0.8),
            processing_time=processing_time
        )
        
        self.db.add(opinion_result)
        
        # OpinionResult를 먼저 커밋하여 foreign key constraint 해결
        self.db.commit()
        self.db.refresh(opinion_result)
        
        # 키워드 저장
        for strength in llm_result.get('strengths', []):
            keyword = OpinionKeyword(
                id=str(uuid.uuid4()),
                opinion_result_id=result_id,
                keyword=strength,
                keyword_type='strength',
                frequency=1.0,  # 추후 개선
                importance=0.8
            )
            self.db.add(keyword)
        
        for weakness in llm_result.get('weaknesses', []):
            keyword = OpinionKeyword(
                id=str(uuid.uuid4()),
                opinion_result_id=result_id,
                keyword=weakness,
                keyword_type='weakness',
                frequency=1.0,
                importance=0.7
            )
            self.db.add(keyword)
        
        # EmployeeResult 업데이트
        employee_result = self.db.query(EmployeeResult).filter(
            EmployeeResult.uid == uid
        ).first()
        
        if employee_result:
            # 하이브리드 점수로 업데이트
            employee_result.text_score = text_scores['text_score']
            employee_result.overall_score = hybrid_score
        
        # 키워드와 EmployeeResult 업데이트 커밋
        self.db.commit()
        
        # 결과 반환
        return OpinionAnalysisResult(
            uid=uid,
            summary=opinion_result.summary,
            strengths=opinion_result.strengths,
            weaknesses=opinion_result.weaknesses,
            text_score=opinion_result.text_score,
            sentiment_score=opinion_result.sentiment_score,
            specificity_score=opinion_result.specificity_score,
            consistency_score=opinion_result.consistency_score,
            dimension_scores=dimension_scores,
            hybrid_score=opinion_result.hybrid_score,
            confidence=opinion_result.confidence,
            years_analyzed=opinion_result.years_analyzed,
            analyzed_at=opinion_result.analyzed_at,
            processing_time=processing_time
        )
    
    async def analyze_batch(
        self, 
        requests: List[OpinionUploadRequest],
        max_concurrent: int = 3,
        batch_size: int = 50
    ) -> List[OpinionAnalysisResult]:
        """
        배치 분석 처리 (최적화된 버전)
        
        Args:
            requests: 분석 요청 리스트
            max_concurrent: 최대 동시 처리 수
            batch_size: 한 번에 처리할 배치 크기
            
        Returns:
            분석 결과 리스트
        """
        results = []
        total = len(requests)
        
        # 배치로 나누어 처리
        for i in range(0, total, batch_size):
            batch = requests[i:i + batch_size]
            batch_end = min(i + batch_size, total)
            logger.info(f"Processing batch {i+1}-{batch_end} of {total}")
            
            # 동시 처리를 위한 세마포어
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_with_semaphore(request):
                async with semaphore:
                    try:
                        return await self.analyze_opinion(request)
                    except Exception as e:
                        logger.error(f"Batch analysis failed for UID {request.uid}: {str(e)}")
                        return None
            
            # 배치 내 요청을 동시에 처리
            tasks = [process_with_semaphore(req) for req in batch]
            batch_results = await asyncio.gather(*tasks)
            
            # None 값 필터링하고 결과 추가
            valid_results = [r for r in batch_results if r is not None]
            results.extend(valid_results)
            
            logger.info(f"Batch complete. Successfully analyzed: {len(valid_results)}/{len(batch)}")
            
            # 배치 간 짧은 대기 (API 부하 방지)
            if i + batch_size < total:
                await asyncio.sleep(0.5)
        
        return results