# AIRISS 평가의견 분석 시스템 아키텍처

## 1. 시스템 개요

AIRISS v4.1에 텍스트 기반 평가의견 분석 기능을 추가하여, 정량적 평가와 정성적 평가를 통합한 하이브리드 스코어링 시스템 구축

## 2. 데이터 플로우

```
[Excel/CSV 업로드] → [데이터 정제] → [LLM 분석] → [점수화] → [DB 저장] → [UI 표시]
```

## 3. 주요 컴포넌트

### 3.1 백엔드 컴포넌트

#### Models (app/models/)
- `opinion_result.py`: 평가의견 분석 결과 DB 모델

#### Schemas (app/schemas/)
- `opinion.py`: API 요청/응답 스키마 정의

#### Services (app/services/)
- `opinion_analysis_service.py`: 핵심 비즈니스 로직
  - 평가의견 정제 및 병합
  - LLM 분석 요청
  - 텍스트 점수화
  - 역량 매핑

#### Core (app/core/)
- `opinion_processor.py`: LLM 기반 텍스트 처리기
  - 요약 생성
  - 키워드 추출
  - 감성 분석

#### API Endpoints (app/api/v1/endpoints/)
- `analysis_opinion.py`: RESTful API 엔드포인트
  - POST /api/v1/analysis/opinion/upload
  - GET /api/v1/analysis/opinion/{uid}
  - POST /api/v1/analysis/opinion/batch

#### Utils (app/utils/)
- `text_cleaning.py`: 텍스트 전처리 유틸리티

#### DB Repositories (app/db/repositories/)
- `opinion_repository.py`: 데이터베이스 CRUD 작업

### 3.2 프론트엔드 컴포넌트

#### Components (airiss-v4-frontend/src/components/)
- `OpinionAnalysisCard.tsx`: 평가의견 분석 결과 카드
- `OpinionUploadModal.tsx`: 평가의견 업로드 모달
- `OpinionScoreChart.tsx`: 텍스트/하이브리드 점수 차트

## 4. 데이터 스키마

### 입력 데이터
```json
{
  "uid": "A001",
  "opinions": {
    "2023": "업무 이해도가 높고 책임감 있게 추진함",
    "2022": null,
    "2021": "팀 내 협업에 기여하고 성과를 창출함"
  }
}
```

### 분석 결과
```json
{
  "uid": "A001",
  "summary": "책임감 있게 업무를 추진하고 협업에도 기여함",
  "strengths": ["추진력", "협업", "책임감"],
  "weaknesses": ["전략적 사고"],
  "text_score": 85.2,
  "sentiment_score": 0.82,
  "specificity_score": 0.78,
  "confidence": 0.93,
  "dimension_scores": {
    "leadership": 87,
    "collaboration": 83,
    "problem_solving": 72,
    "innovation": 68,
    "communication": 80,
    "expertise": 85,
    "execution": 88,
    "growth": 75
  },
  "hybrid_score": 88.6,
  "metadata": {
    "analyzed_at": "2025-07-31T01:00:00Z",
    "model_version": "v1.0",
    "years_analyzed": ["2021", "2023"]
  }
}
```

## 5. 기술 스택

- **백엔드**: FastAPI, SQLAlchemy, Pydantic
- **LLM**: OpenAI GPT-4 (또는 Claude API)
- **데이터 처리**: Pandas, NumPy
- **텍스트 분석**: NLTK/KoNLPy (한국어 처리)
- **프론트엔드**: React, TypeScript, Chart.js

## 6. 보안 및 성능 고려사항

- API Rate Limiting 적용
- 개인정보 마스킹 처리
- 배치 처리 최적화 (100건 단위)
- LLM 응답 캐싱
- 비동기 처리 (Celery 활용 가능)

## 7. 확장 가능성

- 다국어 지원
- 커스텀 역량 프레임워크
- 실시간 분석 대시보드
- 평가의견 자동 생성 (윤리적 가이드라인 준수)