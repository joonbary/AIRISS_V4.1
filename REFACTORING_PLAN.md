# AIRISS v4 리팩터링 계획

## 목표
1. 코드 중복 제거 및 모듈화
2. 명확한 계층 구조 확립
3. 데이터베이스 레이어 통합
4. API 엔드포인트 정리
5. 설정 관리 개선
6. 테스트 구조 체계화

## 새로운 프로젝트 구조

```
airiss_v4_refactored/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # 단일 진입점
│   │   ├── config.py                   # 통합 설정
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py            # 인증 관련
│   │   │   │   ├── analysis.py        # 분석 관련
│   │   │   │   ├── files.py           # 파일 업로드/다운로드
│   │   │   │   └── websocket.py       # WebSocket
│   │   │   └── dependencies.py        # 공통 의존성
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py            # 보안 관련
│   │   │   ├── database.py            # DB 연결 관리
│   │   │   └── exceptions.py          # 커스텀 예외
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # SQLAlchemy Base
│   │   │   ├── user.py
│   │   │   ├── analysis.py
│   │   │   └── file.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── analysis.py
│   │   │   └── file.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── analysis_service.py    # 비즈니스 로직
│   │   │   ├── hybrid_analyzer.py     # AI 분석기
│   │   │   └── file_service.py
│   │   │
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── session.py             # DB 세션 관리
│   │       └── repositories/          # Repository 패턴
│   │           ├── __init__.py
│   │           ├── base.py
│   │           ├── user.py
│   │           └── analysis.py
│   │
│   ├── migrations/                     # Alembic 마이그레이션
│   │   └── versions/
│   │
│   ├── tests/                          # 체계적인 테스트
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   │
│   ├── scripts/                        # 유틸리티 스크립트
│   │   ├── migrate_db.py
│   │   └── create_admin.py
│   │
│   ├── .env.example
│   ├── .env.development
│   ├── .env.production
│   ├── requirements.txt
│   └── docker-compose.yml
│
├── frontend/                           # React 프론트엔드
│   └── (기존 구조 유지)
│
├── docs/                               # 문서화
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DEVELOPMENT.md
│
└── README.md
```

## 리팩터링 단계

### 1단계: 백업 및 정리 (1일)
- 현재 상태 전체 백업
- 불필요한 파일 제거 (.bat 파일들, 백업 파일들)
- 임시 파일 및 테스트 데이터 정리

### 2단계: 데이터베이스 레이어 통합 (2일)
- Repository 패턴 구현
- 단일 DatabaseService로 통합
- PostgreSQL 전용으로 단순화
- 마이그레이션 시스템 정비

### 3단계: API 엔드포인트 정리 (2일)
- 중복 엔드포인트 제거
- RESTful API 규칙 준수
- 버전 관리 체계 확립
- OpenAPI 문서 자동 생성

### 4단계: 서비스 레이어 구조화 (1일)
- 비즈니스 로직 분리
- 의존성 주입 패턴 적용
- 단위 테스트 가능한 구조

### 5단계: 설정 관리 개선 (1일)
- Pydantic Settings 활용
- 환경별 설정 분리
- 비밀 정보 관리 강화

### 6단계: 테스트 및 문서화 (2일)
- 단위 테스트 작성
- 통합 테스트 구현
- API 문서 생성
- 배포 가이드 작성

## 주요 개선 사항

### 1. 단일 진입점
```python
# backend/app/main.py
from fastapi import FastAPI
from app.api.v1 import auth, analysis, files, websocket
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# 라우터 등록
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])
```

### 2. Repository 패턴
```python
# backend/app/db/repositories/analysis.py
class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, analysis_data: dict) -> AnalysisResult:
        # 구현
    
    async def get_by_job_id(self, job_id: str) -> List[AnalysisResult]:
        # 구현
```

### 3. 서비스 레이어
```python
# backend/app/services/analysis_service.py
class AnalysisService:
    def __init__(self, repo: AnalysisRepository, analyzer: HybridAnalyzer):
        self.repo = repo
        self.analyzer = analyzer
    
    async def analyze_file(self, file_id: str, options: dict) -> JobResult:
        # 비즈니스 로직
```

### 4. 설정 관리
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AIRISS v4"
    DATABASE_URL: str
    SECRET_KEY: str
    
    class Config:
        env_file = ".env"
```

## 예상 효과
1. **개발 효율성 향상**: 명확한 구조로 인한 개발 속도 증가
2. **유지보수성 개선**: 코드 중복 제거로 버그 감소
3. **확장성 증대**: 모듈화된 구조로 새 기능 추가 용이
4. **테스트 용이성**: 의존성 주입으로 단위 테스트 가능
5. **배포 단순화**: Docker 기반 표준화된 배포

## 주의사항
- 기존 API 호환성 유지
- 데이터베이스 마이그레이션 시 데이터 무결성 보장
- 점진적 리팩터링으로 서비스 중단 최소화
- 각 단계별 테스트 및 검증 필수