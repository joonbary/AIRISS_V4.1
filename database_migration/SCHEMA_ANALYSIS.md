# AIRISS v4 데이터베이스 스키마 분석 보고서

## 1. 현재 상황 요약

AIRISS v4 프로젝트는 현재 **이중 스키마 구조**로 운영되고 있습니다:
- 레거시 테이블: `results` (기본 분석 결과)
- 신규 테이블: `analysis_results` (AI 피드백 포함)
- 중복 정의: SQLAlchemy 모델과 직접 SQL 정의가 공존

## 2. 주요 문제점

### 2.1 데이터 중복
- 동일한 분석 결과가 두 테이블에 저장
- 데이터 일관성 문제 발생 가능

### 2.2 API 불일치
- 저장: `analysis_results` 테이블 사용
- 조회: `results` 테이블 사용
- 결과적으로 새로운 분석 결과를 조회할 수 없음

### 2.3 스키마 버전 관리 부재
- Alembic 설정은 있으나 제대로 활용되지 않음
- 수동으로 테이블 생성/수정

## 3. 테이블 구조 비교

### 3.1 results 테이블
```sql
- id (SERIAL/TEXT)
- job_id (VARCHAR)
- uid (VARCHAR)
- overall_score (REAL)
- grade (VARCHAR)
- percentile (REAL)
- text_score (REAL)
- quantitative_score (REAL)
- confidence (REAL)
- dimension_scores (TEXT/JSON)
- result_data (TEXT/JSON)
- created_at (TIMESTAMP)
```

### 3.2 analysis_results 테이블
```sql
- id (SERIAL)
- analysis_id (VARCHAR) UNIQUE
- uid (VARCHAR)
- file_id (VARCHAR)
- filename (VARCHAR)
- opinion (TEXT)
- hybrid_score (REAL)
- text_score (REAL)
- quantitative_score (REAL)
- ok_grade (VARCHAR)
- grade_description (TEXT)
- confidence (REAL)
- dimension_scores (JSON)
- ai_feedback (JSON)      -- AI 피드백 추가
- ai_strengths (TEXT)     -- AI 강점 분석 추가
- ai_weaknesses (TEXT)    -- AI 약점 분석 추가
- ai_recommendations (JSON) -- AI 추천사항 추가
- analysis_mode (VARCHAR)
- version (VARCHAR)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

## 4. 통합 방향

### 4.1 단일 테이블로 통합
- `analysis_results`를 기준으로 확장
- 기존 `results` 데이터 마이그레이션
- 모든 API가 통합 테이블 사용

### 4.2 필요한 추가 컬럼
- job_id (results 테이블과의 호환성)
- percentile (순위 정보)
- 인덱스 최적화

### 4.3 데이터 타입 표준화
- PostgreSQL과 SQLite 호환성 고려
- JSON/JSONB 타입 일관성