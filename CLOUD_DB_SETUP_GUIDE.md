# AIRISS v4.1 클라우드 DB 설정 가이드

## 🎯 목표
분석 결과를 Neon DB (PostgreSQL)에 영구적으로 저장하고 조회할 수 있도록 설정합니다.

## 📋 필요 준비사항
1. Neon DB 계정 및 연결 정보
2. Python 환경 (3.8+)
3. 기존 AIRISS v4 프로젝트

## 🚀 빠른 시작

### 1단계: 자동 설정 스크립트 실행
```bash
# 관리자 권한으로 실행
start_with_cloud_db.bat
```

### 2단계: 수동 설정 (필요시)
```bash
# PostgreSQL 패키지 설치
pip install psycopg2-binary asyncpg

# 환경 변수 설정
set DATABASE_TYPE=postgres
set ENABLE_CLOUD_STORAGE=true
```

### 3단계: Neon DB 연결 정보 설정
`.env` 파일에서 다음 내용 수정:
```env
# PostgreSQL 연결 정보 (Neon DB)
POSTGRES_DATABASE_URL=postgresql://neondb_owner:실제패스워드@ep-summer-surf-a153am7x-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

**중요**: 위 URL에서 `***` 부분을 실제 패스워드로 교체해야 합니다.

## 🔧 상세 설정 가이드

### 환경 변수 설정
```env
# 데이터베이스 타입 선택
DATABASE_TYPE=postgres          # postgres 또는 sqlite

# PostgreSQL 연결 (Neon DB)
POSTGRES_DATABASE_URL=postgresql://사용자명:패스워드@호스트/데이터베이스명?sslmode=require

# SQLite (로컬 백업용)
SQLITE_DATABASE_URL=sqlite:///./airiss_v4.db

# 현재 사용할 데이터베이스
DATABASE_URL=${POSTGRES_DATABASE_URL}

# 저장 기능 활성화
ENABLE_CLOUD_STORAGE=true
ANALYSIS_RETENTION_DAYS=365
```

### 데이터베이스 연결 테스트
```python
# 테스트 스크립트
from app.db.database import test_connection, get_database_info

# 연결 정보 확인
info = get_database_info()
print(f"데이터베이스 정보: {info}")

# 연결 테스트
if test_connection():
    print("✅ 연결 성공")
else:
    print("❌ 연결 실패")
```

## 📊 새로운 기능 사용법

### 1. 분석 결과 자동 저장
```python
# 분석 시 자동으로 PostgreSQL에 저장됨
from app.services.hybrid_analyzer import AIRISSHybridAnalyzer

analyzer = AIRISSHybridAnalyzer()
result = analyzer.comprehensive_analysis(
    uid="EMP001",
    opinion="성과가 우수함",
    row_data=employee_data,
    save_to_storage=True,  # 자동 저장 활성화
    file_id="file_123",
    filename="2024년_성과평가.xlsx"
)
```

### 2. 분석 결과 조회
```python
# 저장된 결과 조회
results = analyzer.get_stored_analysis_results(
    file_id="file_123",
    limit=50
)

# 특정 직원 결과 조회
employee_results = analyzer.get_stored_analysis_results(
    uid="EMP001",
    limit=10
)
```

### 3. 통계 및 분석
```python
# 30일간 분석 통계
stats = analyzer.get_analysis_statistics(days=30)
print(f"총 분석 수: {stats['total_analyses']}")
print(f"평균 점수: {stats['average_score']}")
```

## 🌐 API 엔드포인트

### 분석 결과 조회
```bash
# 모든 분석 결과
GET /api/analysis-storage/results

# 특정 파일 결과
GET /api/analysis-storage/results?file_id=file_123

# 특정 직원 결과
GET /api/analysis-storage/results?uid=EMP001
```

### 통계 정보
```bash
# 30일간 통계
GET /api/analysis-storage/statistics?days=30

# 점수 분포
GET /api/analysis-storage/score-distribution?score_type=hybrid_score
```

### 검색 기능
```bash
# 의견 내용 검색
GET /api/analysis-storage/search?search_term=우수&search_type=opinion

# 직원명 검색
GET /api/analysis-storage/search?search_term=EMP001&search_type=uid
```

### 데이터 내보내기
```bash
# JSON 형식
GET /api/analysis-storage/export?format=json

# CSV 형식
GET /api/analysis-storage/export?format=csv
```

## 🛠️ 트러블슈팅

### 연결 실패 시
1. **네트워크 확인**: 방화벽 및 네트워크 설정
2. **연결 문자열 확인**: 사용자명, 패스워드, 호스트 정보
3. **SSL 설정**: `sslmode=require` 필수

### 의존성 오류 시
```bash
# PostgreSQL 드라이버 재설치
pip uninstall psycopg2-binary asyncpg
pip install psycopg2-binary asyncpg

# 또는 바이너리 버전
pip install psycopg2-binary==2.9.7
```

### 성능 이슈 시
- 연결 풀 설정 조정
- 인덱스 최적화
- 배치 처리 활용

## 📈 성능 최적화

### 배치 저장
```python
# 여러 분석 결과 한 번에 저장
batch_data = [
    {"uid": "EMP001", "score": 85.5, ...},
    {"uid": "EMP002", "score": 78.2, ...}
]

for data in batch_data:
    storage_service.save_analysis_result(data)
```

### 인덱스 활용
```sql
-- 자주 사용되는 검색 조건에 인덱스 생성
CREATE INDEX idx_analysis_results_uid ON analysis_results(uid);
CREATE INDEX idx_analysis_results_file_id ON analysis_results(file_id);
CREATE INDEX idx_analysis_results_created_at ON analysis_results(created_at);
```

## 📊 대시보드에서 확인하기

### 브라우저에서 접속
```
http://localhost:8002
```

### 새로운 메뉴
1. **분석 이력**: 과거 분석 결과 조회
2. **통계 대시보드**: 성과 트렌드 및 분포
3. **검색 기능**: 키워드 기반 결과 검색
4. **내보내기**: Excel/CSV 형식으로 다운로드

## 🔐 보안 고려사항

### 데이터 보호
- 연결 문자열 암호화
- 민감 정보 환경변수 관리
- 접근 권한 제한

### 개인정보 보호
- 데이터 익명화 옵션
- 보관 기간 설정 (기본 365일)
- 정기적 데이터 정리

## 📞 지원

### 문제 해결
1. 로그 파일 확인
2. 데이터베이스 상태 점검
3. 연결 테스트 실행

### 추가 지원
- 기술 문의: 개발팀
- 설정 도움: 시스템 관리자
- 기능 요청: 프로덕트 매니저

---

**🎉 완료!** 이제 AIRISS v4.1에서 클라우드 DB를 활용한 영구 저장 기능을 사용할 수 있습니다.
