# AIRISS 데이터베이스 스키마

## 🗄️ SQLite 데이터베이스 구조

### 📋 기존 테이블 (절대 변경 금지)

#### uploaded_files 테이블
```sql
CREATE TABLE uploaded_files (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_size INTEGER,
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT,
    status TEXT DEFAULT 'uploaded'  -- uploaded, analyzing, completed, error
);
```
**제약조건:**
- 🚫 컬럼 삭제/변경 절대 금지
- 🚫 PRIMARY KEY 변경 불가
- ✅ 새 컬럼 추가만 허용 (기존 코드 호환성 유지)

#### analysis_results 테이블
```sql
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT,
    uid TEXT,
    name TEXT,
    department TEXT,
    position TEXT,
    overall_score REAL,
    text_score REAL,
    quantitative_score REAL,
    hybrid_score REAL,
    grade TEXT,
    analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    detailed_scores TEXT,  -- JSON 형태로 8대 차원 점수 저장
    FOREIGN KEY (file_id) REFERENCES uploaded_files (id)
);
```
**제약조건:**
- 🚫 기존 컬럼 스키마 변경 금지
- 🚫 detailed_scores JSON 구조 변경 금지
- ✅ 새 컬럼 추가 허용 (v5 기능용)

---

## 🔮 v5.0 확장 스키마 (추가 예정)

### analysis_results_v5 테이블 (새로 추가)
```sql
CREATE TABLE analysis_results_v5 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER,  -- analysis_results.id와 연결
    deep_learning_scores TEXT,  -- JSON: NLP 모델 결과
    bias_analysis TEXT,  -- JSON: 편향 분석 결과
    prediction_data TEXT,  -- JSON: 예측 분석 결과
    confidence_scores TEXT,  -- JSON: 각 분석의 신뢰도
    ai_insights TEXT,  -- JSON: AI 생성 인사이트
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
);
```

### bias_monitoring 테이블 (새로 추가)
```sql
CREATE TABLE bias_monitoring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT,
    overall_fairness_score REAL,
    gender_bias_score REAL,
    age_bias_score REAL,
    department_bias_score REAL,
    bias_flags TEXT,  -- JSON: 감지된 편향 플래그들
    recommendations TEXT,  -- JSON: 개선 권고사항
    monitored_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES uploaded_files (id)
);
```

### performance_predictions 테이블 (새로 추가)
```sql
CREATE TABLE performance_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER,
    predicted_score_3m REAL,  -- 3개월 후 예측 점수
    predicted_score_6m REAL,  -- 6개월 후 예측 점수
    turnover_risk_score REAL,  -- 이직 위험도
    growth_potential_score REAL,  -- 성장 잠재력
    prediction_confidence REAL,  -- 예측 신뢰도
    model_version TEXT,  -- 사용된 예측 모델 버전
    predicted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analysis_id) REFERENCES analysis_results (id)
);
```

---

## 📊 JSON 스키마 정의

### detailed_scores JSON 구조 (기존 - 변경 금지)
```json
{
  "업무성과": 85.2,
  "리더십협업": 78.5,
  "커뮤니케이션": 82.1,
  "전문성학습": 79.8,
  "태도열정": 88.3,
  "혁신창의": 75.4,
  "고객지향": 81.2,
  "윤리준수": 92.1,
  "confidence": 0.87
}
```

### deep_learning_scores JSON 구조 (v5 새로 추가)
```json
{
  "nlp_model_version": "bert-multilingual-v1",
  "sentiment_analysis": {
    "positive": 0.75,
    "negative": 0.15,
    "neutral": 0.10
  },
  "dimension_scores": {
    "업무성과": {
      "score": 85.2,
      "confidence": 0.91,
      "evidence": ["목표 달성", "효율적 업무"],
      "insights": ["구체적인 성과 지표 언급이 돋보임"]
    }
  }
}
```

### bias_analysis JSON 구조
```json
{
  "overall_fairness": 85.6,
  "demographic_parity": {
    "gender": {"ratio": 0.89, "is_biased": false},
    "age": {"ratio": 0.82, "is_biased": false}
  },
  "detected_issues": [],
  "recommendations": ["성별 균형 우수", "연령대 균형 양호"]
}
```

---

## 🔧 데이터베이스 관리 가이드

### 백업 절차
```sql
-- 일일 백업 (자동화 필요)
.backup backup_YYYYMMDD.db

-- 중요 테이블만 백업
.dump uploaded_files analysis_results > critical_backup.sql
```

### 성능 최적화
```sql
-- 인덱스 생성 (v5 배포 시)
CREATE INDEX idx_analysis_file_id ON analysis_results(file_id);
CREATE INDEX idx_analysis_timestamp ON analysis_results(analysis_timestamp);
CREATE INDEX idx_v5_analysis_id ON analysis_results_v5(analysis_id);
```

### 데이터 정리
```sql
-- 30일 이상된 임시 파일 정리 (자동화 스크립트)
DELETE FROM uploaded_files 
WHERE status = 'uploaded' 
AND upload_timestamp < datetime('now', '-30 days');
```

---

## ⚠️ 중요 제약사항

1. **기존 테이블 스키마 절대 변경 금지**
2. **새 기능은 새 테이블로 분리**
3. **외래키 관계 유지로 데이터 무결성 보장**
4. **JSON 필드 사용으로 유연성 확보**
5. **인덱스 최적화로 성능 유지**

## 🔍 데이터 검증 쿼리

### 기본 상태 확인
```sql
-- 업로드된 파일 현황
SELECT status, COUNT(*) FROM uploaded_files GROUP BY status;

-- 분석 완료 현황  
SELECT DATE(analysis_timestamp), COUNT(*) 
FROM analysis_results 
WHERE analysis_timestamp >= date('now', '-7 days')
GROUP BY DATE(analysis_timestamp);
```

### v5 기능 확인 (배포 후)
```sql
-- 편향 모니터링 현황
SELECT 
  AVG(overall_fairness_score) as avg_fairness,
  COUNT(*) as total_checks
FROM bias_monitoring 
WHERE monitored_at >= date('now', '-1 day');
```
