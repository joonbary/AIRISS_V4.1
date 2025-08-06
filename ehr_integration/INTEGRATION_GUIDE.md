# EHR-AIRISS Integration Guide

## Overview
이 가이드는 EHR 시스템에 AIRISS AI 분석 기능을 통합하는 방법을 설명합니다.

## Architecture
```
EHR System (Frontend)
    ↓
AIRISS Integration Module
    ↓
AIRISS MSA (Railway)
    ↓
OpenAI GPT-3.5
```

## Integration Steps

### 1. Prerequisites
- EHR React 프로젝트
- Node.js 16+ 
- npm or yarn

### 2. Copy Integration Files

필요한 파일들을 EHR 프로젝트로 복사:

```bash
# EHR 프로젝트 루트에서 실행
cp -r airiss_v4/ehr_integration/* ./src/modules/airiss/
cp airiss_v4/EHR_AirissIntegration.jsx ./src/modules/airiss/
cp airiss_v4/ehr_integration_config.js ./src/modules/airiss/
```

### 3. Install Dependencies

```bash
npm install axios
# or
yarn add axios
```

### 4. Import in EHR

#### Main App Integration
```jsx
// src/App.jsx or main component
import EHRAirissIntegration from './modules/airiss/EHR_AirissIntegration';
import './modules/airiss/EHR_AirissIntegration.css';

function App() {
  // EHR 시스템에서 직원 데이터 가져오기
  const employees = useEmployees(); // Your existing hook
  
  return (
    <div className="app">
      {/* Existing EHR components */}
      
      {/* AIRISS Integration - 별도 라우트나 탭으로 추가 */}
      <Route path="/airiss" element={
        <EHRAirissIntegration employees={employees} />
      } />
    </div>
  );
}
```

#### Menu Integration
```jsx
// src/components/Navigation.jsx
<NavLink to="/airiss">
  <Icon name="robot" />
  AIRISS AI 분석
</NavLink>
```

### 5. Employee Data Format

EHR에서 전달하는 직원 데이터 형식:

```javascript
const employeeData = {
  id: "EMP001",
  name: "홍길동",
  department: "개발팀",
  position: "선임개발자",
  
  // Performance metrics (0-100)
  goalAchievement: 85,
  projectSuccess: 90,
  customerSatisfaction: 88,
  attendance: 95,
  
  // Competencies (0-100)
  leadership: 80,
  technical: 85,
  communication: 82,
  problemSolving: 88,
  teamwork: 90,
  creativity: 75,
  adaptability: 85,
  reliability: 92
};
```

### 6. API Endpoints

AIRISS MSA는 다음 엔드포인트를 제공합니다:

- **Health Check**: `GET /health`
- **Single Analysis**: `POST /api/v1/llm/analyze`
- **Batch Analysis**: `POST /api/v1/llm/batch-analyze`
- **API Docs**: `GET /docs`

Base URL: `https://web-production-4066.up.railway.app`

### 7. Environment Variables

EHR `.env` 파일에 추가 (선택사항):

```env
REACT_APP_AIRISS_URL=https://web-production-4066.up.railway.app
REACT_APP_AIRISS_TIMEOUT=30000
```

### 8. Custom Configuration

`ehr_integration_config.js`에서 설정 변경 가능:

```javascript
const AIRISS_CONFIG = {
  baseUrl: process.env.REACT_APP_AIRISS_URL || 'https://web-production-4066.up.railway.app',
  requestConfig: {
    timeout: parseInt(process.env.REACT_APP_AIRISS_TIMEOUT) || 30000,
    retryAttempts: 3
  }
};
```

## Testing

### Local Testing
```bash
# EHR 프로젝트에서
npm start
# Navigate to /airiss route
```

### Test Scenarios
1. Health check 확인
2. 단일 직원 분석
3. 다중 직원 배치 분석
4. 에러 처리 확인

## Monitoring

### Railway Dashboard
- URL: https://railway.app/project/[your-project-id]
- Metrics: CPU, Memory, Request count
- Logs: Real-time application logs

### Health Monitoring
컴포넌트는 자동으로 1분마다 health check를 수행합니다.

## Troubleshooting

### Common Issues

1. **CORS Error**
   - AIRISS MSA는 모든 origin을 허용하도록 설정됨
   - 문제 지속시 Railway 환경변수 확인

2. **Timeout Error**
   - 분석이 30초 이상 걸리는 경우
   - `requestConfig.timeout` 값 증가

3. **Service Unavailable**
   - Railway 서비스 상태 확인
   - Health endpoint 응답 확인

## Support

- AIRISS MSA Logs: Railway Dashboard
- API Documentation: https://web-production-4066.up.railway.app/docs
- OpenAI Status: https://status.openai.com

## Version History

- v1.0.0: Initial EHR-AIRISS integration
- Railway Deployment: web-production-4066