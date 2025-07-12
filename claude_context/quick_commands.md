# AIRISS 빠른 명령어 모음 (Quick Commands)

## 🚀 일상 개발 명령어

### 서버 시작/중지
```bash
# 개발 서버 시작
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# 백그라운드 실행 (Windows)
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

# 배치 파일로 시작
start_airiss_v5.bat

# 프로세스 종료
taskkill /f /im python.exe
```

### 환경 설정
```bash
# 가상환경 활성화
venv_v5\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 의존성 업데이트
pip install --upgrade -r requirements.txt

# 새 패키지 설치 후 freeze
pip install [패키지명]
pip freeze > requirements.txt
```

---

## 🔧 개발 도구 명령어

### 코드 품질
```bash
# 코드 포맷팅
python -m black app/
python -m isort app/

# 타입 체크
python -m mypy app/

# 린팅
python -m flake8 app/

# 보안 스캔
python -m bandit -r app/
```

### 테스트
```bash
# 전체 테스트
python -m pytest tests/ -v

# 특정 파일 테스트
python -m pytest tests/test_hybrid_analyzer.py -v

# 커버리지 확인
python -m pytest tests/ --cov=app --cov-report=html

# 성능 테스트
python -m pytest tests/test_performance.py -v
```

---

## 📊 데이터베이스 관련

### SQLite 명령어
```bash
# DB 파일 확인
sqlite3 instance/airiss.db ".tables"

# 스키마 확인
sqlite3 instance/airiss.db ".schema"

# 데이터 확인
sqlite3 instance/airiss.db "SELECT * FROM uploaded_files LIMIT 5;"

# 백업
copy instance\airiss.db backups\airiss_backup_$(date +%Y%m%d).db
```

### PostgreSQL 명령어 (클라우드)
```bash
# 연결 테스트
python -c "from app.db.database import test_connection; test_connection()"

# 마이그레이션
alembic upgrade head

# 스키마 확인
python -c "from app.db.database import get_db_info; print(get_db_info())"
```

---

## 🐛 디버깅 명령어

### 로그 확인
```bash
# 실시간 로그 모니터링
tail -f logs/app.log

# 에러 로그만 필터링
grep "ERROR" logs/app.log

# 특정 시간대 로그
grep "2024-01-15 14:" logs/app.log
```

### 프로세스 모니터링
```bash
# Python 프로세스 확인
tasklist | findstr python

# 포트 사용 확인
netstat -ano | findstr :8002

# 메모리 사용량 확인
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

---

## 🔄 백업 및 복원

### 파일 백업
```bash
# 전체 프로젝트 백업
tar -czf airiss_backup_$(date +%Y%m%d).tar.gz airiss_v4/

# 핵심 파일만 백업
mkdir backups\$(date +%Y%m%d)
copy app\services\*.py backups\$(date +%Y%m%d)\
copy app\main.py backups\$(date +%Y%m%d)\

# 설정 파일 백업
copy .env .env.backup
copy requirements.txt requirements.backup
```

### Git 작업
```bash
# 현재 상태 저장
git add .
git commit -m "v4.1 안정 버전 백업"
git push origin main

# 새 브랜치 생성
git checkout -b feature/v5-integration

# 변경사항 확인
git status
git diff

# 롤백
git checkout main
git reset --hard HEAD~1
```

---

## 📦 배포 관련

### Railway 배포
```bash
# Railway CLI 로그인
railway login

# 현재 상태 확인
railway status

# 로그 확인
railway logs

# 배포
git push origin main  # 자동 배포 트리거

# 환경변수 확인
railway variables
```

### 로컬 Docker
```bash
# 이미지 빌드
docker build -t airiss:v4.1 .

# 컨테이너 실행
docker run -p 8002:8002 airiss:v4.1

# 컨테이너 내부 접속
docker exec -it [컨테이너ID] /bin/bash

# 이미지 정리
docker system prune -a
```

---

## 🧪 테스트 데이터 관리

### 샘플 데이터 생성
```python
# 테스트 데이터 생성
python scripts/generate_test_data.py --count 100

# 대용량 테스트 데이터
python scripts/generate_test_data.py --count 2000 --file large_test.csv

# 특정 패턴 데이터
python scripts/generate_biased_data.py --bias gender --ratio 0.3
```

### 데이터 검증
```python
# 데이터 품질 체크
python scripts/validate_test_data.py test_data/sample.csv

# 분석 결과 검증
python scripts/verify_analysis_results.py [file_id]

# 성능 벤치마크
python scripts/benchmark_analysis.py --file test_data/large_test.csv
```

---

## 🔍 분석 및 모니터링

### 실시간 분석 상태
```python
# 현재 실행 중인 분석
python -c "from app.db.sqlite_service import SQLiteService; s=SQLiteService(); print(s.get_running_analyses())"

# 분석 성능 통계
python scripts/analysis_stats.py --days 7

# 에러율 확인
python scripts/error_rate_check.py --hours 24
```

### 시스템 헬스체크
```python
# 전체 시스템 상태
python scripts/health_check.py

# API 엔드포인트 테스트
python scripts/test_all_endpoints.py

# 데이터베이스 연결 테스트
python scripts/test_db_connections.py
```

---

## 🛠️ 개발 편의 명령어

### 코드 검색
```bash
# 함수 찾기
grep -r "def analyze_text" app/

# 클래스 찾기  
grep -r "class.*Analyzer" app/

# TODO 찾기
grep -r "TODO\|FIXME\|XXX" app/

# API 엔드포인트 찾기
grep -r "@app\." app/
```

### 파일 관리
```bash
# 임시 파일 정리
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# 로그 파일 정리
find logs/ -name "*.log" -mtime +7 -delete

# 업로드 파일 정리 (주의!)
python scripts/cleanup_old_uploads.py --days 30
```

---

## 🚨 긴급 상황 명령어

### 즉시 서비스 복구
```bash
# 1. 서비스 재시작
taskkill /f /im python.exe
start_airiss_v5.bat

# 2. 데이터베이스 백업에서 복원
copy backups\airiss_latest.db instance\airiss.db

# 3. 설정 초기화
copy .env.example .env
# 환경변수 다시 설정 필요

# 4. 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

### 롤백 프로세스
```bash
# Git 롤백
git checkout main
git reset --hard [안전한_커밋_해시]

# 파일 롤백
copy app\services\hybrid_analyzer_backup.py app\services\hybrid_analyzer.py

# 데이터베이스 롤백
copy backups\airiss_before_v5.db instance\airiss.db
```

---

## 📱 React 프론트엔드 명령어

### 개발 환경
```bash
cd airiss-v4-frontend

# 의존성 설치
npm install

# 개발 서버 시작
npm start

# 빌드
npm run build

# 빌드 결과 백엔드에 복사
xcopy build\* ..\app\static\ /e /y
```

### 패키지 관리
```bash
# 새 패키지 추가
npm install [패키지명]

# 패키지 업데이트
npm update

# 보안 취약점 체크
npm audit
npm audit fix
```

---

## 🎯 v5 개발 전용 명령어

### v5 모듈 테스트
```python
# 딥러닝 모델 다운로드
python scripts/download_v5_models.py

# 편향 탐지 테스트
python -c "from app.services.bias_detection import BiasDetector; print('Bias detection ready')"

# 예측 분석 테스트
python scripts/test_predictive_models.py

# v5 통합 테스트
python scripts/test_v5_integration.py
```

### 성능 벤치마크
```python
# v4 vs v5 성능 비교
python scripts/compare_v4_v5_performance.py

# 메모리 사용량 모니터링
python scripts/memory_monitor.py --duration 600

# GPU 사용량 확인 (선택사항)
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

---

## 🎪 원클릭 작업 명령어

### 전체 프로젝트 상태 확인
```bash
# health_check_all.bat 생성
@echo off
echo "=== AIRISS 전체 상태 확인 ==="
python scripts/health_check.py
python scripts/test_all_endpoints.py  
python scripts/analysis_stats.py --days 1
echo "=== 확인 완료 ==="
pause
```

### 개발 환경 초기화
```bash
# setup_dev_env.bat 생성
@echo off
echo "=== 개발 환경 초기화 ==="
venv_v5\Scripts\activate
pip install -r requirements.txt
python scripts/setup_database.py
echo "=== 초기화 완료 ==="
pause
```

### 빠른 배포
```bash
# quick_deploy.bat (이미 존재)
@echo off
echo "=== 빠른 배포 ==="
git add .
git commit -m "Quick update"
git push origin main
echo "=== Railway 자동 배포 시작 ==="
```

---

## 💡 자주 사용하는 파이썬 스니펫

### 빠른 분석 테스트
```python
# 단일 분석 테스트
from app.services.hybrid_analyzer import AIRISSHybridAnalyzer
analyzer = AIRISSHybridAnalyzer()
result = analyzer.quick_test("좋은 성과를 보여주었습니다")
print(result)

# 파일 분석 테스트
import pandas as pd
df = pd.read_csv("test_data/sample.csv")
results = analyzer.batch_analysis(df)
```

### 빠른 DB 조회
```python
# 최근 분석 결과 확인
from app.db.sqlite_service import SQLiteService
db = SQLiteService()
recent = db.get_recent_analyses(limit=5)
for r in recent: print(f"{r['uid']}: {r['overall_score']}")

# 파일 업로드 현황
files = db.get_recent_uploads(limit=10)
for f in files: print(f"{f['filename']}: {f['status']}")
```

---

## 🔧 환경별 설정 명령어

### 개발 환경 (Development)
```bash
export ENVIRONMENT=development
export DEBUG=True
export LOG_LEVEL=DEBUG
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### 스테이징 환경 (Staging)
```bash
export ENVIRONMENT=staging
export DEBUG=False
export LOG_LEVEL=INFO
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### 프로덕션 환경 (Production)
```bash
export ENVIRONMENT=production
export DEBUG=False
export LOG_LEVEL=WARNING
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 4
```

---

**"효율적인 명령어가 개발 속도를 3배 높입니다!"** ⚡

## 📋 자주 사용하는 커서AI 프롬프트 스니펫

### 빠른 기능 추가
```
app/services/에 [기능명].py 파일을 생성하여 [구체적 기능]을 구현하세요.
기존 hybrid_analyzer.py의 comprehensive_analysis() 함수에 통합하고,
/api/v2/[기능명] 엔드포인트를 추가하세요.
```

### 빠른 버그 수정
```
[에러메시지]가 발생하는 [파일명]의 [함수명]을 수정하세요.
기존 기능은 100% 보존하면서 최소한의 변경으로 문제만 해결하세요.
```

### 빠른 UI 개선
```
dashboard.html에 [새로운 차트/위젯]을 추가하세요.
기존 레이아웃은 유지하면서 Chart.js를 사용하여 구현하세요.
```