# AIRISS v5.0 개발 가이드

## 🚀 빠른 시작

### 1. 애플리케이션 실행
```cmd
# 방법 1: 간단한 실행
start_airiss_v5.bat

# 방법 2: 상세한 검증 후 실행
launch_airiss_v5.bat

# 방법 3: 수동 실행
python app/main.py
```

### 2. 접속 URL
- **메인 페이지**: http://localhost:8002
- **대시보드**: http://localhost:8002/dashboard
- **API 문서**: http://localhost:8002/docs
- **건강 상태**: http://localhost:8002/health

## 📁 프로젝트 구조

```
AIRISS v5.0/
├── app/
│   ├── main.py              # 메인 애플리케이션 파일
│   ├── api/                 # API 라우터
│   ├── core/                # 핵심 설정
│   ├── db/                  # 데이터베이스 관련
│   ├── services/            # 비즈니스 로직
│   ├── templates/           # HTML 템플릿
│   └── static/              # 정적 파일
├── .env                     # 환경 변수 (로컬만)
├── .env.template            # 환경 변수 템플릿
├── requirements.txt         # Python 의존성
└── README.md               # 프로젝트 설명
```

## ⚙️ 환경 설정

### 1. .env 파일 구성
```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=sk-your-actual-openai-key-here

# 데이터베이스 설정
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./airiss_v4.db

# 프로젝트 정보
PROJECT_NAME=AIRISS v5.0
VERSION=5.0.0
```

### 2. API 키 획득
- OpenAI API 키: https://platform.openai.com/api-keys
- 사용량 모니터링: https://platform.openai.com/usage

## 🔧 개발 명령어

### 일반 작업
```cmd
# 서버 시작
python app/main.py

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 초기화
python -c "from app.db.init_db import init_database; init_database()"

# 테스트 실행
python -m pytest tests/
```

### Git 작업
```cmd
# 현재 상태 확인
git status

# 변경사항 커밋
git add .
git commit -m "feat: your feature description"

# 깨끗한 브랜치에 푸시
git push origin v5-clean-final
```

## 🐛 문제 해결

### 1. 일반적인 오류

**오류**: `ModuleNotFoundError: No module named 'app'`
**해결**: 프로젝트 루트 디렉토리에서 실행하세요
```cmd
cd C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4
python app/main.py
```

**오류**: `FileNotFoundError: [Errno 2] No such file or directory: 'main.py'`
**해결**: 올바른 경로로 실행하세요
```cmd
python app/main.py  # main.py가 아닌 app/main.py
```

**오류**: `OpenAI API key not found`
**해결**: .env 파일에 올바른 API 키를 설정하세요

### 2. 포트 충돌
기본 포트 8002가 사용 중인 경우:
```cmd
# 다른 포트로 실행
set PORT=8003
python app/main.py
```

### 3. 데이터베이스 오류
```cmd
# 데이터베이스 파일 삭제 후 재생성
del airiss_v4.db
python app/main.py
```

## 📊 기능 테스트

### 1. 기본 기능 테스트
1. 애플리케이션 시작
2. http://localhost:8002/dashboard 접속
3. 파일 업로드 테스트
4. 분석 결과 확인

### 2. API 테스트
- Swagger UI: http://localhost:8002/docs
- API 엔드포인트 직접 호출 테스트

## 🔒 보안 사항

### 중요한 규칙
1. **.env 파일은 절대 커밋하지 마세요**
2. **실제 API 키는 로컬에만 저장**
3. **템플릿 파일만 버전 관리에 포함**

### 안전한 개발 환경
```cmd
# .gitignore 확인
type .gitignore

# 커밋 전 확인
git status
git diff --staged
```

## 🚀 배포 준비

### 1. 로컬 테스트
```cmd
# 모든 기능 테스트
launch_airiss_v5.bat

# 다양한 브라우저에서 확인
start http://localhost:8002
```

### 2. 프로덕션 준비
- 환경 변수 설정
- 데이터베이스 마이그레이션
- 보안 설정 확인

## 📞 지원

### 개발 지원
- 기술적 문제: GitHub Issues
- 환경 설정: 개발팀 문의
- 긴급 상황: 즉시 연락

### 유용한 리소스
- FastAPI 문서: https://fastapi.tiangolo.com/
- Python 가이드: https://docs.python.org/3/
- Git 가이드: https://git-scm.com/docs
