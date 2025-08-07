# AIRISS v5.0 아키텍처 설계서

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [기술 스택](#기술-스택)
3. [API 엔드포인트 맵](#api-엔드포인트-맵)
4. [컴포넌트 설계](#컴포넌트-설계)
5. [캐싱 전략](#캐싱-전략)
6. [배포 전략](#배포-전략)
7. [테스트 계획](#테스트-계획)

---

## 시스템 개요

### 현재 상태 (AS-IS)
- **백엔드**: FastAPI + OpenAI GPT + NeonDB
- **프론트엔드**: React SPA + 독립 HTML 대시보드
- **배포**: Railway (Docker 컨테이너)
- **문제점**: 
  - React Router와 FastAPI 라우팅 충돌
  - Railway CDN 캐싱 문제
  - 파일 버전 관리 부재

### 목표 상태 (TO-BE)
- **통합 대시보드**: 단일 진입점 `/hr`
- **버전 관리**: 명확한 버전 시스템
- **캐싱 방지**: 동적 콘텐츠 전략
- **모듈화**: 재사용 가능한 컴포넌트

---

## 기술 스택

### Backend
- **Framework**: FastAPI 0.104.1
- **AI**: OpenAI GPT-4 (1.54.5)
- **Database**: PostgreSQL (NeonDB)
- **ORM**: SQLAlchemy 2.0.42
- **PDF**: ReportLab 4.0.7

### Frontend
- **Core**: Vanilla JavaScript (React 없이)
- **차트**: Custom CSS Charts
- **스타일**: CSS3 with Gradient Design
- **아이콘**: Emoji Icons

### Infrastructure
- **호스팅**: Railway.app
- **도메인**: web-production-4066.up.railway.app
- **CI/CD**: GitHub → Railway Auto Deploy

---

## API 엔드포인트 맵

### 1. HR Dashboard APIs
```yaml
GET  /api/v1/hr-dashboard/stats
  Response: {total_employees, promotion_candidates, top_talents, risk_employees}

GET  /api/v1/hr-dashboard/export/pdf
  Response: Binary PDF file

POST /api/v1/hr-dashboard/analyze
  Request: {employee_ids: []}
  Response: {status: "processing", job_id: "xxx"}
```

### 2. Employee APIs
```yaml
GET  /api/v1/employees
  Response: {results: [], total: number}

GET  /api/v1/employees/{id}/ai-analysis
  Response: {employee_name, ai_score, grade, strengths, improvements}

GET  /api/v1/employees/ai-recommendation?type={talent|promotion|risk}
  Response: [{employee_id, name, score, reasons}]
```

### 3. File Upload & Analysis APIs
```yaml
POST /api/v1/upload
  Request: FormData with Excel file
  Response: {file_id, status: "uploaded"}

POST /api/v1/analysis/analyze/{file_id}
  Response: {job_id, status: "processing"}

GET  /api/v1/analysis/status/{job_id}
  Response: {status: "completed", progress: 100}

GET  /api/v1/analysis/results/{job_id}
  Response: {results: [...analyzed data]}
```

### 4. Opinion Analysis APIs
```yaml
POST /api/v1/analysis/opinion/analyze
  Request: {text: string, category: string}
  Response: {sentiment, keywords, insights}
```

---

## 컴포넌트 설계

### 디렉토리 구조
```
app/
├── templates/
│   └── airiss_v5/
│       ├── index.html          # 메인 진입점
│       ├── components/
│       │   ├── dashboard.js    # 대시보드 컴포넌트
│       │   ├── employees.js    # 직원 관리 컴포넌트
│       │   ├── upload.js       # 파일 업로드 컴포넌트
│       │   ├── analysis.js     # 분석 결과 컴포넌트
│       │   └── charts.js       # 차트 컴포넌트
│       └── styles/
│           ├── main.css        # 메인 스타일
│           └── components.css  # 컴포넌트 스타일
```

### 컴포넌트 아키텍처
```javascript
// 모듈 패턴 사용
const AIRISS = {
    version: '5.0.0',
    buildDate: '2025-08-07',
    
    // 컴포넌트 레지스트리
    components: {
        dashboard: null,
        employees: null,
        upload: null,
        analysis: null
    },
    
    // API 클라이언트
    api: {
        baseURL: '/api/v1',
        
        async get(endpoint) {
            const response = await fetch(this.baseURL + endpoint);
            return response.json();
        },
        
        async post(endpoint, data) {
            const response = await fetch(this.baseURL + endpoint, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            return response.json();
        }
    },
    
    // 상태 관리
    state: {
        currentTab: 'dashboard',
        employees: [],
        dashboardStats: {},
        uploadProgress: 0
    },
    
    // 초기화
    init() {
        this.loadComponents();
        this.attachEventListeners();
        this.loadInitialData();
    }
};
```

---

## 캐싱 전략

### 1. 버전 기반 파일명
```javascript
// 빌드 시 자동 생성
const VERSION = Date.now();
const files = {
    css: `/styles/main.css?v=${VERSION}`,
    js: `/js/app.js?v=${VERSION}`
};
```

### 2. HTTP 헤더 설정
```python
@app.get("/hr")
async def serve_dashboard():
    return FileResponse(
        "templates/airiss_v5/index.html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Version": f"5.0.0-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        }
    )
```

### 3. API 응답 캐싱
```javascript
// 5분 캐시
const cache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

async function getCachedData(key, fetcher) {
    const cached = cache.get(key);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
        return cached.data;
    }
    
    const data = await fetcher();
    cache.set(key, { data, timestamp: Date.now() });
    return data;
}
```

---

## 배포 전략

### 1. 환경 변수
```env
# .env.production
API_VERSION=5.0.0
DEPLOYMENT_ENV=production
CACHE_ENABLED=false
DEBUG_MODE=false
```

### 2. 배포 체크리스트
```yaml
Pre-deployment:
  - [ ] 모든 테스트 통과
  - [ ] 버전 번호 업데이트
  - [ ] CHANGELOG 작성
  - [ ] 환경 변수 확인

Deployment:
  - [ ] Git push to main
  - [ ] Railway 빌드 확인
  - [ ] Health check 통과
  - [ ] 캐시 클리어

Post-deployment:
  - [ ] 기능 테스트
  - [ ] 성능 모니터링
  - [ ] 에러 로그 확인
```

### 3. 롤백 계획
```bash
# 롤백 스크립트
#!/bin/bash
PREVIOUS_VERSION="4.0.0"
git checkout tags/v${PREVIOUS_VERSION}
git push origin main --force
```

---

## 테스트 계획

### 1. 단위 테스트
```python
# tests/test_hr_dashboard.py
def test_dashboard_stats():
    response = client.get("/api/v1/hr-dashboard/stats")
    assert response.status_code == 200
    assert "total_employees" in response.json()

def test_employee_analysis():
    response = client.get("/api/v1/employees/123/ai-analysis")
    assert response.status_code == 200
    assert "ai_score" in response.json()
```

### 2. 통합 테스트
```javascript
// tests/integration.test.js
describe('HR Dashboard Integration', () => {
    test('File upload and analysis flow', async () => {
        // 1. Upload file
        const uploadResponse = await uploadFile('test.xlsx');
        expect(uploadResponse.file_id).toBeDefined();
        
        // 2. Start analysis
        const analysisResponse = await startAnalysis(uploadResponse.file_id);
        expect(analysisResponse.job_id).toBeDefined();
        
        // 3. Check status
        const statusResponse = await checkStatus(analysisResponse.job_id);
        expect(statusResponse.status).toBe('completed');
    });
});
```

### 3. E2E 테스트
```javascript
// tests/e2e.test.js
describe('End-to-End User Flow', () => {
    test('Complete user journey', async () => {
        // 1. 대시보드 접속
        await page.goto('/hr');
        await expect(page.title()).toBe('AIRISS v5.0');
        
        // 2. 파일 업로드
        await page.click('#upload-tab');
        await page.setInputFiles('#file-input', 'test.xlsx');
        
        // 3. 분석 실행
        await page.click('#analyze-button');
        await page.waitForSelector('.analysis-complete');
        
        // 4. 결과 확인
        const results = await page.textContent('.results-count');
        expect(parseInt(results)).toBeGreaterThan(0);
    });
});
```

---

## 구현 우선순위

### Phase 1 (즉시)
1. ✅ 기본 대시보드 UI
2. ✅ API 연동
3. ⬜ 파일 업로드 UI

### Phase 2 (1-2일)
1. ⬜ 개인별 상세 분석
2. ⬜ PDF 다운로드
3. ⬜ 실시간 진행 표시

### Phase 3 (3-5일)
1. ⬜ 의견 분석 통합
2. ⬜ 워크플로우 자동화
3. ⬜ 고급 차트/시각화

### Phase 4 (1주)
1. ⬜ 다국어 지원
2. ⬜ 권한 관리
3. ⬜ 감사 로그

---

## 위험 요소 및 대응

### 1. 캐싱 문제
- **위험**: Railway CDN 캐싱
- **대응**: 동적 경로 + 버전 파라미터

### 2. 라우팅 충돌
- **위험**: React Router 간섭
- **대응**: 독립 HTML 페이지 사용

### 3. 성능 이슈
- **위험**: 대용량 데이터 처리
- **대응**: 페이지네이션 + 캐싱

### 4. 보안 취약점
- **위험**: API 키 노출
- **대응**: 환경 변수 + 서버 사이드 처리

---

## 다음 단계

1. **Phase 1 구현 시작**
   - 파일 업로드 컴포넌트 개발
   - API 통합 테스트
   - UI/UX 최적화

2. **문서화**
   - API 문서 자동 생성
   - 사용자 가이드 작성
   - 개발자 문서 업데이트

3. **모니터링 설정**
   - 에러 트래킹 (Sentry)
   - 성능 모니터링 (Datadog)
   - 사용자 분석 (Google Analytics)