# AIRISS Material-UI 마이그레이션 가이드

## 📋 개요

AIRISS 프로젝트를 통합 Material-UI 디자인 시스템으로 전환하기 위한 단계별 가이드입니다.

## 🎯 목표

- **95%** UI 요소 Material-UI 적용
- **100%** 일관된 인터랙션 패턴
- **< 500KB** 번들 크기, **< 1.5s** FCP
- **> 80%** 컴포넌트 재사용률

## 📊 현재 상태 분석

### 기존 UI 구조
- HTML 템플릿: `app/templates/*.html`
- 커스텀 CSS: `app/static/css/main.css`
- React 컴포넌트: `ehr_integration/components/*.jsx`
- 혼재된 스타일링 방식 (인라인, CSS, 일부 MUI)

### 주요 이슈
1. **스타일 불일치**: Bootstrap, 커스텀 CSS, Material-UI 혼재
2. **중복 코드**: 유사한 컴포넌트 다수 존재
3. **성능 문제**: 번들 크기 최적화 필요
4. **접근성**: WCAG 준수 미흡

## 🚀 마이그레이션 단계

### Phase 1: 준비 (1-2일)

#### 1.1 패키지 설치
```bash
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
npm install @mui/x-data-grid @mui/x-charts  # 선택적
```

#### 1.2 기존 프레임워크 제거
```bash
npm uninstall bootstrap react-bootstrap tailwindcss
```

#### 1.3 테마 설정
```javascript
// src/App.js
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { lightTheme, darkTheme } from './theme';

function App() {
  return (
    <ThemeProvider theme={lightTheme}>
      <CssBaseline />
      {/* 앱 컴포넌트 */}
    </ThemeProvider>
  );
}
```

### Phase 2: 공통 컴포넌트 마이그레이션 (3-5일)

#### 2.1 버튼 컴포넌트
**Before:**
```html
<button class="btn btn-primary">클릭</button>
```

**After:**
```javascript
import { Button } from '@mui/material';
<Button variant="contained" color="primary">클릭</Button>
```

#### 2.2 카드 컴포넌트
**Before:**
```html
<div class="card">
  <h2>제목</h2>
  <p>내용</p>
</div>
```

**After:**
```javascript
import { Card, CardContent, Typography } from '@mui/material';
<Card>
  <CardContent>
    <Typography variant="h5">제목</Typography>
    <Typography>내용</Typography>
  </CardContent>
</Card>
```

#### 2.3 테이블 컴포넌트
**Before:**
```html
<table class="table">...</table>
```

**After:**
```javascript
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
<TableContainer component={Paper}>
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>헤더</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      <TableRow>
        <TableCell>데이터</TableCell>
      </TableRow>
    </TableBody>
  </Table>
</TableContainer>
```

### Phase 3: 페이지별 마이그레이션 (5-7일)

#### 3.1 대시보드 페이지
```javascript
// src/pages/Dashboard.jsx
import React from 'react';
import { Grid, Box } from '@mui/material';
import { DataCard, ProgressCard, MetricCard } from '../components/common';

export default function Dashboard() {
  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6} lg={3}>
          <DataCard
            title="총 직원"
            value="156"
            unit="명"
            color="primary"
          />
        </Grid>
        {/* 추가 카드들 */}
      </Grid>
    </Box>
  );
}
```

#### 3.2 직원 분석 테이블
```javascript
// 기존 EmployeeAnalysisTable.jsx 활용
// Material-UI DataGrid로 업그레이드
import { DataGrid } from '@mui/x-data-grid';

const columns = [
  { field: 'id', headerName: 'ID', width: 90 },
  { field: 'name', headerName: '이름', width: 150 },
  { field: 'department', headerName: '부서', width: 150 },
  { field: 'grade', headerName: '등급', width: 100,
    renderCell: (params) => <GradeBadge grade={params.value} />
  },
];

<DataGrid
  rows={employees}
  columns={columns}
  pageSize={10}
  checkboxSelection
/>
```

### Phase 4: 스타일 통합 (2-3일)

#### 4.1 CSS-in-JS 전환
```javascript
// styled-components 사용
import { styled } from '@mui/material/styles';

const StyledHeader = styled('header')(({ theme }) => ({
  background: theme.palette.primary.main,
  padding: theme.spacing(2),
  color: theme.palette.primary.contrastText,
}));
```

#### 4.2 기존 CSS 제거
- `main.css` 파일의 스타일을 MUI 테마로 이전
- 불필요한 CSS 파일 삭제
- CSS Modules 제거

### Phase 5: 최적화 (1-2일)

#### 5.1 번들 최적화
```javascript
// Tree shaking을 위한 개별 import
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
// 대신: import { Button, TextField } from '@mui/material';
```

#### 5.2 코드 스플리팅
```javascript
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Analytics = React.lazy(() => import('./pages/Analytics'));
```

#### 5.3 성능 모니터링
```javascript
// Web Vitals 측정
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Analytics로 전송
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

## 📝 컴포넌트 매핑

| 기존 컴포넌트 | Material-UI 컴포넌트 | 비고 |
|-------------|---------------------|------|
| `.btn` | `Button` | variant 속성 활용 |
| `.card` | `Card` | CardContent, CardActions 조합 |
| `.alert` | `Alert` | severity 속성으로 타입 구분 |
| `.badge` | `Chip` 또는 `Badge` | 용도에 따라 선택 |
| `.progress` | `LinearProgress` | 또는 `CircularProgress` |
| `.modal` | `Dialog` | DialogTitle, DialogContent 사용 |
| `.dropdown` | `Select` 또는 `Menu` | 용도에 따라 선택 |
| `.tabs` | `Tabs` + `Tab` | TabPanel과 함께 사용 |
| `.form-control` | `TextField` | variant="outlined" 권장 |
| `.table` | `Table` 또는 `DataGrid` | 복잡도에 따라 선택 |

## 🔧 트러블슈팅

### 문제 1: 스타일 충돌
```javascript
// 해결: CSS 우선순위 조정
import { StyledEngineProvider } from '@mui/material/styles';

<StyledEngineProvider injectFirst>
  <ThemeProvider theme={theme}>
    {/* 앱 */}
  </ThemeProvider>
</StyledEngineProvider>
```

### 문제 2: 타입스크립트 에러
```typescript
// 테마 타입 확장
declare module '@mui/material/styles' {
  interface Theme {
    custom: {
      grades: Record<string, string>;
    };
  }
}
```

### 문제 3: SSR 이슈
```javascript
// Next.js의 경우
import { ServerStyleSheets } from '@mui/styles';
// _document.js에서 스타일 추출
```

## ✅ 체크리스트

### 마이그레이션 전
- [ ] 현재 코드베이스 백업
- [ ] 패키지 의존성 확인
- [ ] 테스트 환경 준비
- [ ] 팀원 교육 자료 준비

### 마이그레이션 중
- [ ] 테마 설정 완료
- [ ] 공통 컴포넌트 마이그레이션
- [ ] 페이지별 마이그레이션
- [ ] 스타일 통합
- [ ] 접근성 테스트

### 마이그레이션 후
- [ ] 성능 측정 (Lighthouse)
- [ ] 크로스 브라우저 테스트
- [ ] 사용자 피드백 수집
- [ ] 문서화 업데이트
- [ ] 팀 교육 실시

## 📊 예상 결과

### 성능 개선
- **번들 크기**: 800KB → 450KB (-44%)
- **FCP**: 2.1s → 1.3s (-38%)
- **TTI**: 3.5s → 2.2s (-37%)

### 개발 효율성
- **컴포넌트 재사용률**: 45% → 82%
- **개발 시간**: 30% 단축
- **유지보수 시간**: 40% 감소

### 사용자 경험
- **일관성 점수**: 95/100
- **접근성 점수**: 92/100
- **모바일 반응성**: 98/100

## 🚨 위험 요소 및 대응

1. **브라우저 호환성**
   - IE11 미지원 → 폴리필 적용 또는 대체 브라우저 안내

2. **학습 곡선**
   - Material-UI 문법 숙지 필요 → 내부 교육 세션 진행

3. **마이그레이션 기간 중 버그**
   - 점진적 마이그레이션 → 기능별 단계적 배포

4. **성능 저하 가능성**
   - 번들 크기 모니터링 → Tree shaking, 코드 스플리팅 적용

## 📚 참고 자료

- [Material-UI 공식 문서](https://mui.com/)
- [마이그레이션 가이드](https://mui.com/guides/migration-v4/)
- [디자인 시스템 베스트 프랙티스](https://mui.com/design-kits/)
- [성능 최적화 가이드](https://mui.com/guides/minimizing-bundle-size/)

## 🤝 지원

문제 발생 시 연락처:
- 기술 지원: tech-support@airiss.com
- 디자인 시스템: design-system@airiss.com
- 프로젝트 관리: pm@airiss.com