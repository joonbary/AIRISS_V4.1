# AIRISS 프로젝트 클린업 리포트

## 📊 분석 일시
- **실행일**: 2024-01-15
- **모드**: Safe Mode (안전 모드)
- **프로젝트 경로**: D:\AIRISS_project_clean

## 📁 프로젝트 현황
- **Python 파일**: 100+ 개
- **HTML 템플릿**: 21개
- **중복/임시 파일**: 약 40개 식별

## 🧹 클린업 대상 (안전 모드)

### 1. 임시/테스트 파일 (삭제 권장)
```
✅ 안전하게 삭제 가능:
- test_js_error.html
- test_airiss.html  
- test_design.html
- find_template_error.py
- find_syntax_error.py
- check_syntax.py
- app/templates/debug_test.html
- app/templates/api_test.html
- app/templates/responsive_test.html
- app/templates/airiss_v5_test.html
```

### 2. 백업/이전 버전 파일 (아카이브 권장)
```
📦 백업 폴더로 이동 권장:
- app/main_backup.py
- app/main_broken.py
- app/main_emergency_minimal.py
- app/main_emergency_simple.py
- app/main_current.py
- app/main_v2.py
- app/main_v4.py
- app/main_fixed.py
- app/main_v4_fixed.py
- app/main_simple.py
- app/main_no_auth.py
```

### 3. 중복 API 파일 (통합 필요)
```
⚠️ 검토 후 통합:
- app/api/search.py (원본)
- app/api/search_fixed.py (수정 버전)
- app/api/search_fixed_v2.py (재수정 버전)

- app/api/analysis.py (원본)
- app/api/analysis_v2.py (v2)
- app/api/v1/endpoints/analysis_fixed.py (수정 버전)
```

### 4. 오래된 대시보드 템플릿 (아카이브 권장)
```
📦 templates_archive 폴더로 이동:
- app/templates/hr_dashboard_simple.html
- app/templates/hr_dashboard_working.html
- app/templates/hr_dashboard_v2.html
- app/templates/hr_dashboard_v3.html
- app/templates/hr_dashboard_2025_01_07.html
- app/templates/hr_dashboard_final.html
- app/templates/dashboard_latest.html
```

## 📈 클린업 효과 예상

### Before
- 총 파일 수: ~150개
- 중복 코드: ~40%
- 프로젝트 크기: ~25MB

### After (예상)
- 총 파일 수: ~100개 (-33%)
- 중복 코드: ~10% (-75%)
- 프로젝트 크기: ~15MB (-40%)

## 🛡️ 안전 조치

1. **백업 생성**
   ```bash
   # 전체 백업 생성
   cp -r D:\AIRISS_project_clean D:\AIRISS_project_clean_backup_20240115
   ```

2. **아카이브 폴더 구조**
   ```
   _archive/
   ├── main_versions/     # main.py 이전 버전들
   ├── templates_old/     # 오래된 템플릿들
   ├── api_deprecated/    # 사용하지 않는 API
   └── test_files/        # 테스트 파일들
   ```

3. **Git 커밋**
   ```bash
   git add -A
   git commit -m "chore: 프로젝트 클린업 전 백업 커밋"
   ```

## ✅ 권장 실행 순서

### Phase 1: 테스트 파일 제거 (낮은 위험)
```bash
# 테스트 파일 삭제
rm test_*.html
rm find_*.py
rm check_*.py
```

### Phase 2: 아카이브 폴더 생성 및 이동 (중간 위험)
```bash
# 아카이브 폴더 생성
mkdir -p _archive/main_versions
mkdir -p _archive/templates_old
mkdir -p _archive/api_deprecated

# 파일 이동
mv app/main_*.py _archive/main_versions/
mv app/templates/hr_dashboard_*.html _archive/templates_old/
```

### Phase 3: Import 최적화 (낮은 위험)
- 사용하지 않는 import 제거
- 중복 import 통합
- import 순서 정리 (표준 라이브러리 → 서드파티 → 로컬)

## 🚫 건드리지 말아야 할 파일

**핵심 파일 (절대 삭제 금지)**:
- `app/main.py` - 메인 애플리케이션
- `app/main_msa.py` - MSA 버전 (사용 중)
- `app/templates/airiss_v5.html` - 현재 사용 중인 대시보드
- `app/db/database.py` - 데이터베이스 연결
- `app/models/employee.py` - 직원 모델
- `.env` - 환경 변수

## 📋 체크리스트

- [ ] 백업 생성 완료
- [ ] Git 커밋 완료
- [ ] 테스트 파일 삭제
- [ ] 아카이브 폴더 생성
- [ ] main.py 변형들 이동
- [ ] 템플릿 이전 버전 이동
- [ ] Import 최적화
- [ ] 동작 테스트
- [ ] 최종 커밋

## 💡 추가 권장사항

1. **README.md 업데이트**
   - 프로젝트 구조 문서화
   - 주요 파일 설명 추가

2. **.gitignore 업데이트**
   ```
   _archive/
   *.backup
   test_*.html
   *_test.py
   ```

3. **의존성 정리**
   ```bash
   pip freeze > requirements_current.txt
   # 사용하지 않는 패키지 제거
   ```

## 🎯 예상 소요 시간
- 안전 모드: 약 30분
- 전체 작업: 약 1시간

---

**주의**: 이 리포트는 안전 모드 기준입니다. 
실제 삭제 전 반드시 백업을 생성하고, 각 파일이 실제로 사용되지 않는지 확인하세요.