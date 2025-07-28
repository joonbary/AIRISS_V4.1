# AIRISS v4.0 - AI Risk Intelligent Scoring System

## 개요
AIRISS는 OK Financial Group의 인사 평가 분석 시스템입니다. AI 기반의 텍스트 분석과 정량적 데이터 분석을 통해 종합적인 인사 평가를 수행합니다.

## 주요 기능
- 📊 **Excel/CSV 파일 업로드 및 분석**
- 🤖 **AI 기반 텍스트 평가 분석**
- 📈 **정량적 데이터 분석**
- 📥 **분석 결과 다운로드 (Excel/CSV/JSON)**
- 🔄 **실시간 분석 진행률 표시**

## 기술 스택
### Backend
- FastAPI (Python 3.10+)
- SQLite (개발) / PostgreSQL (운영)
- Pandas, NumPy
- OpenAI API (선택적)

### Frontend
- React 18
- TypeScript
- Material-UI
- WebSocket

## 설치 및 실행

### 사전 요구사항
- Python 3.10 이상
- Node.js 18 이상
- npm 또는 yarn

### 백엔드 설정
```bash
# 가상환경 생성
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
copy .env.example .env
# .env 파일을 열어 필요한 설정 입력
```

### 프론트엔드 설정
```bash
cd airiss-v4-frontend
npm install
```

### 실행
```bash
# Windows
start.cmd

# 또는 개별 실행
# 백엔드
python -m app.main

# 프론트엔드
cd airiss-v4-frontend
npm start
```

## 접속 정보
- Frontend: http://localhost:3000
- Backend API: http://localhost:8006
- API Documentation: http://localhost:8006/docs
- WebSocket: ws://localhost:8006/connect

## 프로젝트 구조
```
airiss_v4/
├── app/                    # 백엔드 애플리케이션
│   ├── api/               # API 엔드포인트
│   ├── core/              # 핵심 설정 및 의존성
│   ├── db/                # 데이터베이스 관련
│   ├── models/            # 데이터 모델
│   ├── schemas/           # Pydantic 스키마
│   └── services/          # 비즈니스 로직
├── airiss-v4-frontend/    # 프론트엔드 애플리케이션
│   ├── src/               # React 소스 코드
│   └── public/            # 정적 파일
├── uploads/               # 업로드된 파일
├── results/               # 분석 결과
└── tests/                 # 테스트 코드
```

## API 엔드포인트
- `POST /api/v1/files/upload` - 파일 업로드
- `GET /api/v1/files/list` - 파일 목록 조회
- `POST /api/v1/analysis/start/{file_id}` - 분석 시작
- `GET /api/v1/analysis/status/{job_id}` - 분석 상태 조회
- `GET /api/v1/analysis/download/{job_id}` - 결과 다운로드

## 개발 가이드
- [API 문서](http://localhost:8006/docs)
- [프로젝트 정리 리포트](./CLEANUP_REPORT.md)

## 라이선스
OK Financial Group 내부 사용 전용
