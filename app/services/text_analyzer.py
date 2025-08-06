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
import time
import os

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
            logger.info(f"✅ 한국어 BERT 모델 로드 성공: {model_name}")
        except ImportError:
            logger.warning("⚠️ Transformers 라이브러리 없음 - BERT 기반 분석 비활성화")
            self.bert_model = None
        except Exception as e:
            logger.error(f"BERT 모델 로드 실패: {e}")
            self.bert_model = None
        
        # 편향성 탐지기 초기화
        from app.services.bias_detection import BiasDetector
        self.bias_detector = BiasDetector()
    
    async def analyze_text(
        self, 
        uid: str, 
        opinion: str,
        enable_ai: bool = False,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """텍스트 분석 및 AI 피드백 생성 통합 함수"""
        
        # 1. 기본 텍스트 분석 수행
        basic_analysis = await self._perform_basic_analysis(uid, opinion)
        
        # 2. AI 피드백 생성 (활성화된 경우)
        ai_feedback = {}
        if enable_ai and api_key:
            logger.info(f"🤖 AI 피드백 생성 시작 - UID: {uid}")
            ai_feedback = await self.generate_ai_feedback(
                uid, opinion, api_key, model, max_tokens
            )
            logger.info(f"✅ AI 피드백 생성 완료 - UID: {uid}")
        else:
            logger.info(f"⚠️ AI 피드백 건너뜀 - enable_ai: {enable_ai}, api_key: {'있음' if api_key else '없음'}")
        
        # 3. 결과 통합
        return {
            **basic_analysis,
            "ai_feedback": ai_feedback
        }
    
    async def _perform_basic_analysis(self, uid: str, opinion: str) -> Dict[str, Any]:
        """기본 텍스트 분석"""
        
        # 텍스트 전처리
        cleaned_text = self._preprocess_text(opinion)
        
        # 8대 영역별 분석
        dimension_results = {}
        for dimension, config in self.framework.items():
            score = self._analyze_dimension(cleaned_text, config)
            dimension_results[dimension] = {
                "score": score,
                "weight": config["weight"],
                "weighted_score": score * config["weight"]
            }
        
        # 종합 점수 계산
        overall_score = sum(r["weighted_score"] for r in dimension_results.values())
        
        # 감정 분석
        sentiment = self._analyze_sentiment(cleaned_text)
        
        # 키워드 추출
        keywords = self._extract_keywords(cleaned_text)
        
        return {
            "uid": uid,
            "overall_score": round(overall_score, 1),
            "dimension_scores": dimension_results,
            "sentiment": sentiment,
            "keywords": keywords,
            "text_length": len(cleaned_text),
            "analysis_version": "AIRISS v4.1"
        }
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 기본 정리
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        return text.strip()
    
    def _analyze_dimension(self, text: str, config: Dict) -> float:
        """개별 영역 분석"""
        positive_score = 0
        negative_score = 0
        
        # 긍정 키워드 매칭
        for keyword in config["keywords"]["positive"]:
            if keyword in text:
                positive_score += 1
        
        # 부정 키워드 매칭
        for keyword in config["keywords"]["negative"]:
            if keyword in text:
                negative_score += 1
        
        # 점수 계산 (0-100)
        if positive_score + negative_score == 0:
            return 50.0  # 중립
        
        score = (positive_score / (positive_score + negative_score)) * 100
        return min(100, max(0, score))
    
    def analyze_text(self, opinion: str, dimension: str) -> Dict:
        """특정 차원에 대한 텍스트 분석 (기존 hybrid_analyzer 호환용)"""
        if dimension not in self.framework:
            return {
                "score": 50.0, 
                "confidence": 50,
                "signals": {
                    "positive_words": [],
                    "negative_words": []
                }
            }
        
        config = self.framework[dimension]
        text = self._preprocess_text(opinion)
        score = self._analyze_dimension(text, config)
        
        # 키워드 매칭 결과 수집
        positive_words = []
        negative_words = []
        
        for keyword in config["keywords"]["positive"]:
            if keyword in text:
                positive_words.append(keyword)
        
        for keyword in config["keywords"]["negative"]:
            if keyword in text:
                negative_words.append(keyword)
        
        return {
            "score": score,
            "confidence": 70,
            "signals": {
                "positive_words": positive_words[:5],  # 최대 5개
                "negative_words": negative_words[:5]   # 최대 5개
            }
        }
    
    def calculate_overall_score(self, dimension_scores: Dict[str, float]) -> Dict:
        """8대 영역 점수를 종합하여 최종 점수 계산"""
        
        # 가중치 적용
        weighted_score = 0
        total_weight = 0
        
        for dimension, score in dimension_scores.items():
            if dimension in self.framework:
                weight = self.framework[dimension]["weight"]
                weighted_score += score * weight
                total_weight += weight
        
        # 최종 점수 계산
        if total_weight > 0:
            overall_score = weighted_score / total_weight
        else:
            overall_score = 50.0
        
        # 등급 계산
        if overall_score >= 90:
            grade = "S"
        elif overall_score >= 80:
            grade = "A"
        elif overall_score >= 70:
            grade = "B"
        elif overall_score >= 60:
            grade = "C"
        elif overall_score >= 50:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "confidence": 75  # 기본 신뢰도
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """감정 분석"""
        positive_words = ["좋다", "우수", "뛰어나다", "훌륭", "최고"]
        negative_words = ["나쁘다", "부족", "미흡", "문제", "개선"]
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        total = pos_count + neg_count
        if total == 0:
            return {"positive": 0.5, "negative": 0.5, "neutral": 0.0}
        
        return {
            "positive": pos_count / total,
            "negative": neg_count / total,
            "neutral": 0.0
        }
    
    def _extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """키워드 추출"""
        words = text.split()
        word_freq = Counter(words)
        
        # 불용어 제거
        stopwords = {"은", "는", "이", "가", "을", "를", "의", "에", "에서", "으로", "와", "과"}
        filtered_words = [(word, freq) for word, freq in word_freq.items() 
                         if word not in stopwords and len(word) > 1]
        
        # 상위 키워드 반환
        sorted_words = sorted(filtered_words, key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_n]]
    
    async def generate_ai_feedback(
        self,
        uid: str,
        opinion: str,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1500
    ) -> Dict[str, Any]:
        """OpenAI를 사용한 고급 AI 피드백 생성 (재시도 로직 포함)"""
        
        if not self.openai_available:
            logger.error("OpenAI 모듈이 설치되지 않았습니다.")
            return self._get_fallback_response("OpenAI 모듈 미설치")
        
        if not api_key:
            logger.error("OpenAI API 키가 제공되지 않았습니다.")
            return self._get_fallback_response("API 키 없음")
        
        # 재시도 로직
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 OpenAI API 호출 시도 {attempt + 1}/{max_retries} - UID: {uid}")
                
                # API 키 유효성 검증
                if not api_key:
                    logger.error("API 키가 없습니다")
                    raise ValueError("OpenAI API 키가 제공되지 않았습니다.")
                
                # API 키 정리 (공백 제거)
                cleaned_api_key = api_key.strip()
                
                # API 키 형식 검증 (sk-로 시작하는지 확인)
                if not cleaned_api_key.startswith('sk-') and not cleaned_api_key.startswith('sess-'):
                    logger.error(f"잘못된 API 키 형식: {cleaned_api_key[:10]}...")
                    raise ValueError("올바른 OpenAI API 키 형식이 아닙니다.")
                
                # OpenAI 클라이언트 생성 (타임아웃 설정 추가)
                try:
                    import httpx
                    # Railway 환경에서 연결 시간 증가
                    client = self.openai.OpenAI(
                        api_key=cleaned_api_key,
                        timeout=httpx.Timeout(60.0, connect=30.0),  # 연결 타임아웃 30초, 전체 60초
                        max_retries=2  # 재시도 횟수 제한
                    )
                except Exception as client_error:
                    logger.error(f"OpenAI 클라이언트 생성 실패: {client_error}")
                    raise ValueError(f"API 클라이언트 초기화 실패: {str(client_error)}")
                
                # 프롬프트 생성
                prompt = self._create_analysis_prompt(uid, opinion)
                
                # 프록시 사용 시도 (항상 시도, Railway 환경이 아니어도 가능)
                logger.info("🔄 OpenAI API 호출: 프록시 연결 시도")
                try:
                    response = await self._use_internal_proxy(prompt, model, max_tokens)
                    if response:
                        logger.info("✅ 내부 프록시를 통한 OpenAI API 호출 성공")
                    else:
                        raise Exception("프록시 응답이 비어있음")
                except Exception as proxy_error:
                    logger.warning(f"⚠️ 내부 프록시 실패, 직접 연결 시도: {proxy_error}")
                    # 프록시 실패시 직접 연결 시도
                    response = await self._direct_openai_call(client, prompt, model, max_tokens)
                
                # 응답 처리
                if response and response.choices and len(response.choices) > 0:
                    feedback = response.choices[0].message.content
                    logger.info(f"✅ OpenAI API 호출 성공 - UID: {uid}")
                    return self._parse_ai_response(feedback)
                else:
                    logger.error("OpenAI API 응답이 비어있습니다")
                    raise ValueError("API 응답 없음")
                    
            except asyncio.TimeoutError:
                logger.warning(f"⏱️ OpenAI API 타임아웃 (시도 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                return self._get_fallback_response("API 타임아웃")
                
            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__
                logger.error(f"❌ OpenAI API 오류 (시도 {attempt + 1}/{max_retries})")
                logger.error(f"   오류 타입: {error_type}")
                logger.error(f"   오류 메시지: {error_msg}")
                
                # 연결 실패 처리
                if "connection" in error_msg.lower():
                    logger.error("🔥 OpenAI API 연결 실패")
                    logger.error("   가능한 원인:")
                    logger.error("   1. 네트워크 정책으로 외부 API 호출 차단")
                    logger.error("   2. OpenAI 서버 일시적 문제")
                    logger.error("   3. 네트워크 타임아웃")
                    logger.info("💡 해결 방법: AI 분석을 비활성화하고 진행하거나 네트워크 설정을 확인하세요")
                
                # API 키 관련 오류 처리
                if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    logger.error("API 키 인증 실패")
                    return self._get_fallback_response("API 키 인증 실패 - 올바른 API 키를 설정해주세요")
                
                # 재시도 가능한 오류인지 확인
                if "connection" in error_msg.lower() or "timeout" in error_msg.lower() or "network" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1)
                        logger.info(f"⏳ {wait_time}초 후 재시도...")
                        await asyncio.sleep(wait_time)  # 지수 백오프
                        continue
                
                # 속도 제한 오류
                if "rate" in error_msg.lower() or "limit" in error_msg.lower():
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # 지수 백오프
                        logger.info(f"⏳ 속도 제한 - {wait_time}초 후 재시도...")
                        await asyncio.sleep(wait_time)
                        continue
                
                # 재시도 불가능한 오류
                return self._get_fallback_response(f"AI 분석 오류: {error_msg}")
        
        # 모든 재시도 실패
        logger.error(f"❌ OpenAI API 호출 최종 실패 - UID: {uid}")
        return self._get_fallback_response("최대 재시도 횟수 초과")
    
    async def _use_internal_proxy(self, prompt: str, model: str, max_tokens: int) -> Any:
        """내부 프록시를 통한 OpenAI API 호출"""
        import httpx
        
        # Railway 환경에서는 localhost 사용
        base_url = "http://localhost:8080"
        
        request_data = {
            "model": model,
            "messages": [
                {
                    "role": "system", 
                    "content": "당신은 OK금융그룹의 수석 HR 전문가입니다. 건설적이고 실행 가능한 피드백을 제공하세요."
                },
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/api/v1/proxy/openai/chat/completions",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                # OpenAI 응답 형식으로 변환
                if "choices" in result:
                    return type('MockResponse', (), {
                        'choices': [type('Choice', (), {
                            'message': type('Message', (), {
                                'content': result["choices"][0]["message"]["content"]
                            })()
                        })()]
                    })()
                else:
                    raise Exception("Invalid response format")
            else:
                raise Exception(f"프록시 오류: {response.status_code}")
    
    async def _direct_openai_call(self, client, prompt: str, model: str, max_tokens: int) -> Any:
        """직접 OpenAI API 호출"""
        import asyncio
        
        # 타임아웃을 30초로 설정
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "당신은 OK금융그룹의 수석 HR 전문가입니다. 건설적이고 실행 가능한 피드백을 제공하세요."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7,
                    timeout=30  # 30초 타임아웃
                )
            ),
            timeout=35  # asyncio 타임아웃은 약간 더 길게
        )
        return response
    
    def _create_analysis_prompt(self, uid: str, opinion: str) -> str:
        """AI 분석용 프롬프트 생성"""
        return f"""
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
    
    def _parse_ai_response(self, feedback: str) -> Dict[str, Any]:
        """AI 응답 파싱"""
        sections = {
            "strengths": "",
            "weaknesses": "",
            "overall": "",
            "action_plan": []
        }
        
        try:
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
            else:
                # 구조화되지 않은 응답 처리
                sections["overall"] = feedback.strip()
                
        except Exception as e:
            logger.error(f"AI 응답 파싱 오류: {e}")
            sections["overall"] = feedback.strip()
        
        return {
            "ai_strengths": sections["strengths"],
            "ai_weaknesses": sections["weaknesses"],
            "ai_feedback": sections["overall"],
            "ai_recommendations": sections["action_plan"],
            "error": None
        }
    
    def _get_fallback_response(self, error_reason: str) -> Dict[str, Any]:
        """오류 시 폴백 응답"""
        logger.warning(f"AI 분석 폴백 응답 사용: {error_reason}")
        
        # 오류 타입별 메시지
        if "connection" in error_reason.lower():
            message = "OpenAI API 연결에 실패했습니다. 네트워크 설정을 확인하거나 AI 분석을 비활성화하고 진행하세요."
        elif "timeout" in error_reason.lower():
            message = "OpenAI API 응답 시간 초과. 네트워크 상태를 확인하거나 AI 분석을 비활성화하세요."
        elif "api" in error_reason.lower() and "key" in error_reason.lower():
            message = "OpenAI API 키가 유효하지 않습니다. 환경변수를 확인하세요."
        elif "rate" in error_reason.lower():
            message = "OpenAI API 요청 한도 초과. 잠시 후 다시 시도하거나 AI 분석을 비활성화하세요."
        else:
            message = f"AI 분석 실패: {error_reason}. AI 분석을 비활성화하고 진행하세요."
        
        return {
            "ai_strengths": "텍스트 기반 분석으로 대체되었습니다.",
            "ai_weaknesses": "AI 분석 없이 기본 평가만 제공됩니다.",
            "ai_feedback": message,
            "ai_recommendations": ["텍스트 분석 결과를 참고하여 평가해주세요."],
            "error": error_reason
        }


class BiasDetector:
    """편향성 탐지 클래스"""
    
    def __init__(self):
        self.bias_patterns = {
            "gender": ["여성", "남성", "여자", "남자", "그녀", "그"],
            "age": ["나이", "연령", "젊은", "늙은", "신입", "경력"],
            "appearance": ["외모", "생김새", "키", "몸무게", "체격"],
            "personal": ["결혼", "자녀", "가족", "종교", "정치"]
        }
    
    def detect_bias(self, text: str) -> Dict[str, Any]:
        """편향성 탐지"""
        detected_biases = []
        
        for bias_type, keywords in self.bias_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    detected_biases.append({
                        "type": bias_type,
                        "keyword": keyword,
                        "severity": "medium"
                    })
        
        return {
            "has_bias": len(detected_biases) > 0,
            "bias_count": len(detected_biases),
            "detected_biases": detected_biases,
            "bias_score": min(100, len(detected_biases) * 20)
        }