# AIRISS 파일 구조 상세 맵핑

## 📁 전체 디렉토리 구조

```
C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4\
├── 🔧 설정 파일들
│   ├── .env ⚠️ (환경변수 - 보안 주의)
│   ├── .env.example ✅ (환경변수 템플릿)
│   ├── requirements.txt ✅ (Python 의존성)
│   ├── Dockerfile ✅ (컨테이너 설정)
│   ├── Procfile ✅ (Railway 배포 설정)
│   ├── railway.json ✅ (Railway 설정)
│   └── runtime.txt ✅ (Python 버전)
│
├── 📱 프론트엔드
│   └── airiss-v4-frontend/ ✅ (React SPA)
│       ├── build/ ✅ (빌드된 정적 파일들)
│       ├── src/ ✅ (React 소스코드)
│       ├── package.json ✅ (Node.js 의존성)
│       └── public/ ✅ (공개 파일들)
│
├── 🎯 백엔드 코어
│   └── app/
│       ├── main.py 🔥 (FastAPI 메인 앱)
│       ├── __init__.py ✅ (패키지 초기화)
│       │
│       ├── 🔌 API 라우터들
│       │   ├── analysis.py ✅ (분석 API)
│       │   ├── upload.py ✅ (파일 업로드)
│       │   ├── analysis_storage.py ✅ (저장 관리)
│       │   ├── websocket.py ✅ (실시간 통신)
│       │   ├── search.py ✅ (검색 기능)
│       │   └── user.py ✅ (사용자 관리)
│       │
│       ├── 🧠 핵심 서비스들
│       │   ├── hybrid_analyzer.py 🔥 (메인 분석 엔진)
│       │   ├── text_analyzer.py 🔥 (텍스트 분석 프레임워크)
│       │   ├── quantitative_analyzer.py 🔥 (정량 분석)
│       │   ├── analysis_service.py ✅ (분석 서비스)
│       │   ├── analysis_storage_service.py ✅ (저장 서비스)
│       │   ├── excel_service.py ✅ (엑셀 처리)
│       │   │
│       │   ├── 🔍 편향 탐지 (v5)
│       │   │   └── bias_detection/ 🚧
│       │   │       ├── __init__.py
│       │   │       ├── bias_detector.py 🚧
│       │   │       ├── fairness_metrics.py 🚧
│       │   │       └── bias_patterns.json 🚧
│       │   │
│       │   ├── 🔮 예측 분석 (v5)
│       │   │   └── predictive_analytics/ 🚧
│       │   │       ├── __init__.py
│       │   │       ├── performance_predictor.py 🚧
│       │   │       ├── turnover_predictor.py 🚧
│       │   │       └── growth_analyzer.py 🚧
│       │   │
│       │   └── 🌐 외부 연동
│       │       └── aws/ ✅
│       │           ├── s3_service.py ✅
│       │           └── __init__.py ✅
│       │
│       ├── 🗄️ 데이터베이스
│       │   ├── database.py ✅ (DB 연결 관리)
│       │   ├── sqlite_service.py ✅ (SQLite 헬퍼)
│       │   └── __init__.py ✅
│       │
│       ├── 📊 데이터 모델
│       │   ├── analysis_result.py ✅ (분석 결과 모델)
│       │   ├── upload_file.py ✅ (업로드 파일 모델)
│       │   └── __init__.py ✅
│       │
│       ├── 🛠️ 유틸리티
│       │   ├── encoding_safe.py ✅ (인코딩 안전성)
│       │   ├── file_utils.py ✅ (파일 처리)
│       │   └── __init__.py ✅
│       │
│       └── 🎨 템플릿 (폴백용)
│           ├── dashboard.html ✅ (대시보드 템플릿)
│           └── error.html ✅ (에러 페이지)
│
├── 📂 데이터 저장소
│   ├── uploads/ ✅ (업로드된 파일들)
│   ├── static/ ✅ (정적 파일들)
│   └── test_data/ ✅ (테스트 데이터)
│
├── 🧪 테스트
│   ├── tests/ ✅ (테스트 파일들)
│   └── test_data/ ✅ (테스트용 샘플)
│
├── 📚 문서화
│   ├── docs/ ✅ (프로젝트 문서)
│   ├── claude_context/ ✅ (클로드 지침서들)
│   ├── README.md ✅ (프로젝트 소개)
│   ├── CHANGELOG.md ✅ (변경 이력)
│   └── CONTRIBUTING.md ✅ (기여 가이드)
│
└── 🔨 운영 스크립트들
    ├── start_airiss_v5.bat ✅ (서버 시작)
    ├── quick_deploy.bat ✅ (빠른 배포)
    ├── cleanup_project.py ✅ (프로젝트 정리)
    └── [기타 100+ 운영 스크립트들]
```

---

## 🔥 핵심 파일 상세 분석

### 1. main.py (FastAPI 메인 앱)
```python
역할: 전체 애플리케이션의 진입점
중요도: ★★★★★ (절대 변경 금지)
의존성: 모든 라우터와 서비스들
특징:
- Railway 클라우드 최적화
- Windows/OneDrive 인코딩 안전성
- PostgreSQL 클라우드 DB 연동
- React SPA 라우팅 지원
- WebSocket 실시간 통신
```

### 2. hybrid_analyzer.py (메인 분석 엔진)
```python
역할: 텍스트+정량 하이브리드 분석의 핵심
중요도: ★★★★★ (절대 변경 금지)
의존성: text_analyzer, quantitative_analyzer
주요 함수:
- comprehensive_analysis() ← 모든 분석의 시작점
- calculate_hybrid_score() ← 종합 점수 계산
- generate_insights() ← 인사이트 생성
v5 확장 지점: 새 분석 모듈 통합
```

### 3. text_analyzer.py (텍스트 분석 프레임워크)
```python
역할: 8대 차원 텍스트 분석 프레임워크
중요도: ★★★★★ (핵심 로직 변경 금지)
특징:
- 8대 차원별 키워드 프레임워크
- 감정 분석 및 의미 추출
- 점수 정규화 및 가중치 적용
v5 확장: 딥러닝 NLP 모델 통합 예정
```

### 4. quantitative_analyzer.py (정량 분석)
```python
역할: 수치 데이터 기반 정량 분석
중요도: ★★★★☆ (확장 가능)
기능:
- 성과 지표 정량화
- 통계적 분석
- 벤치마킹 및 비교
v5 확장: 고급 통계 모델 추가
```

---

## 🔌 API 라우터 상세

### analysis.py
```python
엔드포인트: /api/analysis/*
역할: 분석 실행 및 결과 조회
주요 라우트:
- POST /api/analysis/{file_id} ← 분석 시작
- GET /api/analysis/{file_id}/status ← 분석 상태
- GET /api/analysis/{file_id}/result ← 결과 조회
의존성: hybrid_analyzer, analysis_service
```

### upload.py
```python
엔드포인트: /api/upload
역할: 파일 업로드 및 데이터 추출
지원 형식: CSV, XLSX
최대 크기: 50MB
보안: 파일 형식 검증, 바이러스 스캔
```

### analysis_storage.py
```python
엔드포인트: /api/analysis-storage/*
역할: 분석 결과 영구 저장 관리
데이터베이스: PostgreSQL 클라우드
기능: CRUD, 검색, 통계, 내보내기
```

### websocket.py
```python
엔드포인트: /websocket
역할: 실시간 양방향 통신
용도: 분석 진행률, 알림, 실시간 업데이트
프로토콜: WebSocket over HTTP/HTTPS
```

---

## 🗄️ 데이터베이스 구조

### 핵심 테이블들
```sql
uploaded_files:
- id (PK)
- filename 
- upload_time
- file_path
- status
- user_id

analysis_results:
- id (PK)
- file_id (FK)
- uid (직원 ID)
- overall_score
- grade
- confidence
- dimension_scores (JSON)
- insights (TEXT)
- created_at

analysis_jobs:
- id (PK)
- file_id (FK)
- status
- progress
- started_at
- completed_at
- error_message
```

### v5 확장 테이블들 (준비 중)
```sql
bias_detection_results:
- id (PK)
- analysis_id (FK)
- bias_type
- severity
- affected_groups
- recommendations

predictive_models:
- id (PK)
- model_type
- version
- accuracy
- training_data
- parameters (JSON)
```

---

## 🎨 프론트엔드 구조

### React 컴포넌트 구조
```
airiss-v4-frontend/src/
├── components/
│   ├── Dashboard.jsx ← 메인 대시보드
│   ├── FileUpload.jsx ← 파일 업로드 UI
│   ├── AnalysisResults.jsx ← 결과 표시
│   ├── Charts/ ← Chart.js 차트들
│   │   ├── RadarChart.jsx ← 8대 차원 레이더
│   │   ├── HistogramChart.jsx ← 점수 분포
│   │   └── ProgressChart.jsx ← 진행률
│   └── Common/ ← 공통 컴포넌트들
│
├── services/
│   ├── api.js ← API 호출 서비스
│   ├── websocket.js ← WebSocket 관리
│   └── storage.js ← 로컬 스토리지
│
├── styles/
│   ├── dashboard.css ← 대시보드 스타일
│   ├── charts.css ← 차트 스타일
│   └── common.css ← 공통 스타일
│
└── utils/
    ├── formatters.js ← 데이터 포맷팅
    ├── validators.js ← 입력 검증
    └── constants.js ← 상수 정의
```

---

## 🔧 설정 파일 상세

### .env (환경변수)
```bash
⚠️ 보안 주의 - 절대 Git에 커밋 금지

# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8002
PORT=8002  # Railway 동적 포트

# 데이터베이스
DATABASE_URL=postgresql://[보안정보]
POSTGRES_HOST=[호스트]
POSTGRES_DB=[DB명]
POSTGRES_USER=[사용자]
POSTGRES_PASSWORD=[비밀번호]

# React 빌드
REACT_BUILD_PATH=./airiss-v4-frontend/build

# AWS (선택)
AWS_ACCESS_KEY_ID=[키]
AWS_SECRET_ACCESS_KEY=[시크릿]
S3_BUCKET_NAME=[버킷명]
```

### requirements.txt (Python 의존성)
```txt
# 핵심 프레임워크
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0

# 데이터베이스
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.13.1

# 데이터 처리
pandas==2.1.4
numpy==1.24.3
openpyxl==3.1.2

# AI/ML (v5 준비)
scikit-learn==1.3.2
transformers==4.36.2
torch==2.1.2

# 웹소켓
python-socketio==5.10.0
python-multipart==0.0.6

# 유틸리티
python-dotenv==1.0.0
```

---

## 🛠️ 주요 유틸리티 파일들

### encoding_safe.py
```python
역할: Windows/OneDrive 인코딩 문제 해결
주요 함수:
- safe_path_join() ← 안전한 경로 조합
- safe_exists_check() ← 파일 존재 확인
- get_safe_base_dir() ← 프로젝트 루트 확인
```

### file_utils.py
```python
역할: 파일 처리 유틸리티
기능:
- 파일 형식 검증
- 크기 제한 확인
- 임시 파일 관리
- 자동 정리
```

---

## 🚧 v5 개발 영역

### bias_detection/ (편향 탐지)
```python
🚧 개발 중인 모듈들:
- bias_detector.py ← 편향 탐지 메인 엔진
- fairness_metrics.py ← 공정성 지표 계산
- bias_patterns.json ← 편향 패턴 데이터

예상 통합 지점:
- hybrid_analyzer.py의 comprehensive_analysis()에 통합
- 새로운 API 엔드포인트: /api/v2/bias-check
```

### predictive_analytics/ (예측 분석)
```python
🚧 개발 중인 모듈들:
- performance_predictor.py ← 성과 예측
- turnover_predictor.py ← 이직 위험도
- growth_analyzer.py ← 성장 잠재력

예상 통합 지점:
- 별도 분석 파이프라인으로 구성
- 새로운 API: /api/v2/predict/*
```

---

## 📋 파일 중요도 분류

### 🔥 절대 변경 금지 (Critical)
```
- main.py
- hybrid_analyzer.py  
- text_analyzer.py
- quantitative_analyzer.py
- API 라우터들 (upload.py, analysis.py 등)
- 데이터베이스 스키마
```

### ⚠️ 신중한 변경 (Careful)
```
- 서비스 파일들 (analysis_service.py 등)
- 유틸리티 파일들
- 설정 파일들
- React 컴포넌트들
```

### ✅ 자유로운 확장 (Expandable)
```
- v5 관련 새 모듈들
- 새로운 유틸리티
- 추가 API 엔드포인트
- 새로운 차트/UI 컴포넌트
- 테스트 파일들
```

---

## 🎯 커서AI 작업시 파일 참조 가이드

### 새 기능 추가시
```python
1. 새 모듈 생성: app/services/v5_[기능명].py
2. 기존 통합: hybrid_analyzer.py에 import 추가
3. API 라우터: app/api/v2/[기능명].py
4. 테스트: tests/test_[기능명].py
```

### 버그 수정시
```python
1. 문제 파일 백업: [원본파일].backup
2. 최소한의 변경으로 수정
3. 기존 테스트 통과 확인
4. 새 테스트 케이스 추가
```

### UI 개선시
```javascript
1. React 컴포넌트: airiss-v4-frontend/src/components/
2. 스타일 추가: airiss-v4-frontend/src/styles/
3. 기존 레이아웃 보존
4. 반응형 고려
```

---

**"정확한 파일 구조 이해가 안전한 개발의 시작입니다!"** 📁