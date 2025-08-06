# AIRISS v4 데이터베이스 마이그레이션 가이드

## 📋 개요

이 가이드는 AIRISS v4의 분산된 데이터베이스 스키마를 통합하는 과정을 설명합니다.

### 현재 문제점
- `results` 테이블과 `analysis_results` 테이블이 중복되어 사용
- API 저장/조회 불일치로 인한 데이터 누락
- AI 분석 결과가 제대로 저장/조회되지 않음

### 해결 방안
- 두 테이블을 `analysis_results_v2`로 통합
- 호환성을 위한 뷰(View) 제공
- 점진적 마이그레이션 전략

## 🚀 마이그레이션 단계

### 1단계: 준비 작업

```bash
# 백업 디렉토리 생성
mkdir -p database_migration/backups

# 현재 데이터 확인
python check_postgres_results.py
```

### 2단계: 마이그레이션 실행

```bash
# 마이그레이션 스크립트 실행
python database_migration/migration_script.py
```

스크립트는 다음 작업을 자동으로 수행합니다:
1. 현재 데이터 백업 (JSON 형식)
2. 새 통합 테이블 생성
3. 데이터 마이그레이션
4. 호환성 뷰 생성
5. 데이터 무결성 검증

### 3단계: 애플리케이션 코드 업데이트

마이그레이션 후 다음 파일들을 수정해야 합니다:

#### 3.1 데이터베이스 서비스 수정
`app/db/__init__.py`:
- `save_analysis_result()`: analysis_results_v2 테이블 사용
- `get_analysis_results()`: analysis_results_v2 테이블 조회

#### 3.2 API 엔드포인트 수정
`app/api/analysis.py`:
- 결과 조회 시 새 테이블 사용

### 4단계: 테스트

```bash
# 통합 테스트 실행
python test_ai_analysis_debug.py

# 데이터베이스 확인
python check_migration_status.py
```

## 📊 스키마 변경사항

### 통합된 필드 매핑

| 기존 테이블.필드 | 새 테이블.필드 | 설명 |
|---------------|--------------|-----|
| results.overall_score | analysis_results_v2.overall_score | 종합 점수 |
| analysis_results.hybrid_score | analysis_results_v2.overall_score | 동일 값 |
| results.grade | analysis_results_v2.ok_grade | 등급 |
| results.result_data | analysis_results_v2.result_data | 전체 결과 JSON |

### 새로 추가된 필드
- `job_id`: results 테이블과의 호환성
- `ai_error`: AI 처리 오류 메시지
- `percentile`: 순위 정보

## 🔄 롤백 절차

문제 발생 시 롤백:

```bash
# 롤백 스크립트 실행
python database_migration/rollback.py

# 또는 수동으로
DROP TABLE IF EXISTS analysis_results_v2;
DROP VIEW IF EXISTS results_view;
DROP VIEW IF EXISTS analysis_results_view;
```

## ⚠️ 주의사항

1. **백업 필수**: 마이그레이션 전 반드시 백업
2. **점진적 적용**: 프로덕션은 단계별로 적용
3. **호환성 유지**: 뷰를 통해 기존 API 호환성 유지
4. **모니터링**: 마이그레이션 후 성능 모니터링

## 📝 체크리스트

- [ ] 데이터베이스 백업 완료
- [ ] 마이그레이션 스크립트 실행
- [ ] 데이터 무결성 검증
- [ ] 애플리케이션 코드 수정
- [ ] 테스트 통과
- [ ] 프로덕션 배포
- [ ] 모니터링 설정
- [ ] 기존 테이블 정리 (선택사항)

## 🆘 문제 해결

### 마이그레이션 실패 시
1. 로그 확인: `database_migration/backups/migration_log_*.json`
2. 백업에서 복원
3. 문제 수정 후 재시도

### 성능 이슈
1. 인덱스 확인
2. 쿼리 최적화
3. 필요시 추가 인덱스 생성

## 📞 지원

문제 발생 시:
- 로그 파일 확인
- 백업 데이터 활용
- 점진적 롤백 전략 적용