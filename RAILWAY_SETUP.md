# Railway 환경변수 설정 가이드

## OpenAI API 키 설정 방법

### 1. OpenAI API 키 생성
1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. 로그인 후 "Create new secret key" 클릭
3. 키 이름 입력 (예: "AIRISS-Railway")
4. 생성된 키 복사 (⚠️ 한 번만 표시되므로 안전한 곳에 저장!)

### 2. Railway에 환경변수 설정

#### Railway 대시보드에서 설정:
1. [Railway 대시보드](https://railway.app) 로그인
2. AIRISS 프로젝트 선택
3. 왼쪽 메뉴에서 "Variables" 클릭
4. "Add Variable" 버튼 클릭
5. 다음 변수들을 추가:

```bash
# 필수 환경변수
OPENAI_API_KEY=sk-proj-여기에_실제_API_키_입력
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1500

# 선택적 환경변수 (이미 설정되어 있을 수 있음)
DATABASE_URL=postgresql://...
PORT=8003
```

#### Railway CLI에서 설정:
```bash
# Railway CLI 설치 (아직 없다면)
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 연결
railway link

# 환경변수 설정
railway variables set OPENAI_API_KEY=sk-proj-여기에_실제_API_키_입력
railway variables set OPENAI_MODEL=gpt-3.5-turbo
railway variables set OPENAI_MAX_TOKENS=1500

# 재배포 트리거
railway up
```

### 3. 환경변수 확인
설정 후 Railway 로그에서 다음과 같은 메시지를 확인:
```
✅ OpenAI API 키 로드됨: sk-proj-rR3...OacA
```

### 4. 문제 해결

#### API 키가 여전히 인식되지 않는 경우:
1. Railway Variables 페이지에서 키가 올바르게 저장되었는지 확인
2. 재배포 트리거: Railway 대시보드에서 "Redeploy" 버튼 클릭
3. 로그 확인: Railway 대시보드 "Deployments" → 최신 배포 → "View Logs"

#### 401 Authentication Error가 발생하는 경우:
- API 키가 만료되었거나 삭제되었을 수 있음
- OpenAI 대시보드에서 새 키 생성 필요
- 사용량 한도 초과 여부 확인

### 5. 보안 주의사항
- ⚠️ API 키를 코드에 직접 하드코딩하지 마세요
- ⚠️ API 키를 공개 저장소에 커밋하지 마세요
- ✅ 항상 환경변수를 통해 관리하세요
- ✅ Railway의 환경변수는 암호화되어 안전하게 저장됩니다

### 6. 비용 관리
- OpenAI API는 사용량 기반 과금
- GPT-3.5-turbo: $0.0015 / 1K input tokens, $0.002 / 1K output tokens
- 월별 사용량 한도 설정 권장: OpenAI 대시보드 → Usage limits

## 환경변수 우선순위

시스템은 다음 순서로 API 키를 찾습니다:
1. **Railway 환경변수** (최우선)
2. 클라이언트가 제공한 API 키
3. .env 파일 (로컬 개발용)

Railway 환경변수를 설정하면 클라이언트가 API 키를 입력할 필요가 없습니다!