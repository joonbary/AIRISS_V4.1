# AIRISS 배포 가이드

## 🚀 현재 배포 환경

### Production 환경
- **URL**: https://web-production-4066.up.railway.app/
- **플랫폼**: Railway.app
- **현재 버전**: v4.1 (안정 운영 중)
- **Python**: 3.11+
- **Database**: SQLite (프로덕션용)

### Development 환경  
- **로컬 경로**: C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
- **포트**: 8002 (기본값)
- **실행 방법**: run.bat 또는 python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

---

## 📋 배포 전 체크리스트

### 🔍 코드 품질 검증
- [ ] 모든 기존 API 엔드포인트 정상 작동 확인
- [ ] 새 기능 단위 테스트 통과
- [ ] 성능 테스트 (응답시간 5초 이내)
- [ ] 메모리 누수 없음 확인
- [ ] 보안 취약점 스캔 완료

### 📊 데이터 백업
- [ ] SQLite 데이터베이스 백업
- [ ] 업로드된 파일들 백업
- [ ] 설정 파일 백업
- [ ] 환경변수 문서화

### 🔧 의존성 관리
- [ ] requirements.txt 업데이트
- [ ] Python 버전 호환성 확인
- [ ] 새 패키지 라이선스 검토
- [ ] 보안 패치 적용

---

## 🔄 배포 절차

### Step 1: 로컬 테스트
```bash
# 1. 가상환경 활성화
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 로컬 서버 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002

# 4. 기능 테스트
curl http://localhost:8002/health
```

### Step 2: Railway 배포 준비
```bash
# 1. Railway CLI 설치 (최초 1회)
npm install -g @railway/cli

# 2. Railway 로그인
railway login

# 3. 프로젝트 연결
railway link [PROJECT_ID]
```

### Step 3: 배포 실행
```bash
# 1. 코드 푸시 (자동 배포 트리거)
git add .
git commit -m "v5.0 기능 추가: [구체적 변경사항]"
git push origin main

# 2. 배포 상태 모니터링
railway status
railway logs
```

### Step 4: 배포 후 검증
```bash
# 1. Production 헬스체크
curl https://web-production-4066.up.railway.app/health

# 2. 주요 기능 테스트
curl -X POST https://web-production-4066.up.railway.app/api/upload

# 3. 실시간 로그 모니터링
railway logs --follow
```

---

## 🔒 환경 변수 관리

### Production 환경변수 (Railway)
```env
# 기본 설정
PYTHON_VERSION=3.11
PORT=8002
NODE_ENV=production

# 데이터베이스
DATABASE_URL=sqlite:///./airiss_prod.db

# v5 기능 토글
ENABLE_V5_FEATURES=false
V5_ROLLOUT_PERCENTAGE=0

# 보안
SECRET_KEY=your_secret_key_here
ADMIN_API_KEY=your_admin_key_here

# AI 모델 설정
MODEL_CACHE_PATH=/tmp/models
USE_GPU=false

# 로깅
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Development 환경변수 (.env)
```env
# 개발 환경 설정
ENVIRONMENT=development
DEBUG=true
PORT=8002

# 로컬 데이터베이스
DATABASE_URL=sqlite:///./airiss_dev.db

# v5 기능 (개발용)
ENABLE_V5_FEATURES=true
V5_ROLLOUT_PERCENTAGE=100

# 개발용 키
SECRET_KEY=dev_secret_key
ADMIN_API_KEY=dev_admin_key
```

---

## 🚨 롤백 절차

### 긴급 롤백 (5분 이내)
```bash
# 1. 이전 버전으로 즉시 롤백
railway rollback [DEPLOYMENT_ID]

# 2. 상태 확인
curl https://web-production-4066.up.railway.app/health

# 3. 로그 확인
railway logs --tail 100
```

### 데이터베이스 롤백
```bash
# 1. 백업에서 복원
cp backup_YYYYMMDD.db airiss_prod.db

# 2. 애플리케이션 재시작
railway restart
```

---

## 📊 모니터링 및 알림

### 핵심 메트릭
- **응답 시간**: 평균 < 3초, 95%ile < 5초
- **에러율**: < 1%
- **메모리 사용량**: < 512MB
- **디스크 사용량**: < 1GB

### 알림 설정
```yaml
# Railway 알림 (설정 예시)
alerts:
  - type: "high_error_rate"
    threshold: "5%"
    duration: "5m"
  - type: "high_response_time" 
    threshold: "10s"
    duration: "2m"
  - type: "memory_usage"
    threshold: "80%"
    duration: "10m"
```

### 로그 분석
```bash
# 에러 로그 필터링
railway logs | grep "ERROR"

# 특정 API 성능 분석
railway logs | grep "/api/analyze"

# 사용자 활동 분석
railway logs | grep "POST\|GET"
```

---

## 🔧 Blue-Green 배포 (v5.0 대규모 업데이트용)

### 준비 단계
1. **Green 환경 구성**: 새 Railway 프로젝트 생성
2. **코드 배포**: v5.0 코드를 Green 환경에 배포
3. **데이터 동기화**: 최신 DB를 Green에 복사
4. **테스트 실행**: Green 환경에서 전체 테스트

### 전환 단계
```bash
# 1. DNS/프록시 설정 변경
# Blue: web-production-4066.up.railway.app (기존)
# Green: web-production-v5.up.railway.app (신규)

# 2. 트래픽 점진적 전환
# 10% → 25% → 50% → 100%

# 3. 모니터링 강화
railway logs --project=GREEN --follow
```

### 완료 단계
- Blue 환경 백업 후 제거
- Green을 새로운 Production으로 설정
- 모니터링 대시보드 업데이트

---

## 🆘 장애 대응 플레이북

### 장애 유형별 대응

#### 1. 서버 다운 (HTTP 5xx)
```bash
# 즉시 조치
railway restart
railway logs --tail 50

# 원인 분석
grep "ERROR\|CRITICAL" logs.txt
```

#### 2. 성능 저하 (느린 응답)
```bash
# 리소스 사용량 확인
railway metrics

# 프로세스 재시작
railway restart

# 데이터베이스 최적화
sqlite3 airiss_prod.db "VACUUM;"
```

#### 3. 분석 실패 (AI 모델 오류)
```bash
# v5 기능 비활성화
railway env set ENABLE_V5_FEATURES=false

# v4 모드로 폴백
railway restart
```

---

## 📈 성능 최적화

### 서버 최적화
```python
# uvicorn 설정 최적화
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8002 \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-log \
  --log-level info
```

### 데이터베이스 최적화
```sql
-- 정기 유지보수 (매주 실행)
PRAGMA optimize;
VACUUM;
REINDEX;

-- 성능 모니터링
PRAGMA table_info(analysis_results);
```

### 정적 파일 최적화
- CSS/JS 파일 압축
- 이미지 최적화
- 브라우저 캐싱 설정

---

## 🔐 보안 체크리스트

### 배포 전 보안 검증
- [ ] 환경변수 하드코딩 제거
- [ ] API 키 보안 저장
- [ ] SQL 인젝션 방지
- [ ] XSS 보호 설정
- [ ] CORS 정책 적용
- [ ] HTTPS 강제 설정

### 정기 보안 점검
- 의존성 취약점 스캔 (매월)
- 보안 패치 적용 (즉시)
- 액세스 로그 분석 (매주)
- 침입 탐지 모니터링

이제 배포 관련 모든 절차가 체계화되었습니다! 🚀
