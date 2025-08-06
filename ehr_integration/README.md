# AIRISS EHR Integration Guide

## 개요
이 모듈은 AIRISS LLM 분석 기능을 기존 EHR 시스템에 통합하기 위한 React 컴포넌트와 서비스를 제공합니다.

## 디렉토리 구조
```
ehr_integration/
├── services/
│   └── airissService.js        # AIRISS API 통신 서비스
├── context/
│   └── AirissContext.jsx       # React Context for 상태 관리
├── components/
│   ├── ExecutiveDashboard.jsx  # 경영진 대시보드
│   └── EmployeeAnalysisTable.jsx # 직원 분석 테이블
├── example/
│   └── App.jsx                 # EHR 통합 예제
├── AirissModule.jsx            # 메인 통합 모듈
├── package.json                # 의존성 관리
└── README.md                   # 이 파일
```

## 빠른 시작

### 1. 설치
```bash
# EHR 프로젝트 내에서
npm install ./path/to/ehr_integration

# 또는 개별 파일 복사
cp -r ehr_integration/* your-ehr-project/src/modules/airiss/
```

### 2. 환경 설정
```javascript
// .env
REACT_APP_AIRISS_URL=http://localhost:8080  // AIRISS 마이크로서비스 URL
AIRISS_API_KEY=your_api_key_here           // 선택사항: API 키
```

### 3. 기본 통합
```jsx
// EHR App.jsx
import AirissModule from './modules/airiss/AirissModule';

function App() {
  const employees = [...]; // EHR 시스템의 직원 데이터
  const userRole = 'manager'; // 현재 사용자 권한
  
  return (
    <Routes>
      {/* 기존 EHR 라우트 */}
      <Route path="/hr/airiss" element={
        <AirissModule employees={employees} userRole={userRole} />
      } />
    </Routes>
  );
}
```

### 4. 라우터 기반 통합
```jsx
import { AirissRoutes } from './modules/airiss/AirissModule';

function App() {
  return (
    <Routes>
      {/* AIRISS 서브 라우트 */}
      <Route path="/hr/airiss/*" element={
        <AirissRoutes employees={employees} userRole={userRole} />
      } />
    </Routes>
  );
}
```

## 주요 컴포넌트

### AirissModule
메인 통합 모듈로 탭 기반 네비게이션 제공
```jsx
<AirissModule
  employees={employeeArray}  // 직원 데이터 배열
  userRole="manager"         // 사용자 권한
/>
```

### AirissProvider
Context API를 통한 상태 관리
```jsx
<AirissProvider>
  {/* AIRISS 컴포넌트들 */}
</AirissProvider>
```

### ExecutiveDashboard
경영진용 대시보드 (통계, 차트, 인사이트)
- 전체 직원 AI 점수 분포
- 등급별 통계
- Top Performers
- 개선 필요 인원

### EmployeeAnalysisTable
직원 분석 테이블 (검색, 필터, 상세보기)
- 개별/배치 AI 분석
- 필터링 및 검색
- CSV 내보내기
- 상세 분석 보기

## API 서비스

### airissService.js
AIRISS 마이크로서비스와 통신하는 서비스 레이어

```javascript
import airissService from './services/airissService';

// 단일 직원 분석
const result = await airissService.analyzeEmployee(employeeData);

// 배치 분석
const results = await airissService.batchAnalyzeEmployees(employeeList);

// 헬스 체크
const health = await airissService.checkHealth();
```

## 데이터 변환

### EHR → AIRISS 형식
```javascript
// EHR 직원 데이터
const ehrEmployee = {
  id: 'EMP001',
  firstName: '철수',
  lastName: '김',
  dept: '개발팀',
  jobTitle: '과장',
  // ...
};

// AIRISS 형식으로 자동 변환
const airissFormat = {
  employee_id: 'EMP001',
  name: '김철수',
  department: '개발팀',
  position: '과장',
  performance_data: {...},
  competencies: {...}
};
```

## 권한 관리

### 역할별 접근 권한
- `admin`: 모든 기능 접근 가능
- `executive`: 경영진 대시보드 접근
- `manager`: 대시보드 및 직원 분석
- `hr`: 직원 분석 기능
- `employee`: 제한된 접근

```jsx
// 권한 체크 예제
const canViewDashboard = ['admin', 'executive', 'manager'].includes(userRole);
```

## 커스터마이징

### 테마 적용
```jsx
import { ThemeProvider, createTheme } from '@mui/material';

const ehrTheme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' }
  }
});

<ThemeProvider theme={ehrTheme}>
  <AirissModule />
</ThemeProvider>
```

### 캐싱 설정
```javascript
const service = new AirissService({
  cacheTimeout: 600000, // 10분
  retryAttempts: 5,
  timeout: 60000
});
```

## 테스트

### 개발 서버 실행
```bash
cd ehr_integration/example
npm install
npm run dev
```

### 통합 테스트
```bash
# AIRISS 마이크로서비스 실행
cd airiss_v4
python -m uvicorn app.main_msa:app --port 8080

# EHR 앱 실행
cd ehr_integration
npm run dev
```

## 배포

### 프로덕션 빌드
```bash
npm run build
```

### 환경별 설정
```javascript
// production.env
REACT_APP_AIRISS_URL=https://airiss-api.company.com
AIRISS_API_KEY=production_key
```

## 모니터링

### 서비스 상태 확인
- 자동 헬스 체크 (1분 간격)
- 서비스 상태 표시기
- 에러 알림

### 성능 메트릭
- API 응답 시간
- 캐시 적중률
- 분석 성공/실패율

## 문제 해결

### CORS 오류
AIRISS 마이크로서비스의 CORS 설정 확인:
```python
# .env.msa
ALLOWED_ORIGINS=https://ehr.company.com
```

### 인증 실패
- API 키 확인
- JWT 토큰 유효성 확인
- 네트워크 접근 권한 확인

### 느린 응답
- 캐싱 활성화
- 배치 크기 조정
- 네트워크 지연 확인

## 지원
문제가 있으시면 GitHub 이슈를 생성하거나 관리자에게 문의하세요.