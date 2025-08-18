# AIRISS Design System v4.0

## 🎨 디자인 철학

AIRISS 디자인 시스템은 **일관성**, **접근성**, **확장성**을 핵심 가치로 합니다.

### 핵심 원칙
1. **일관성 (Consistency)**: 모든 인터페이스에서 동일한 패턴과 컴포넌트 사용
2. **접근성 (Accessibility)**: WCAG 2.1 AA 기준 준수
3. **확장성 (Scalability)**: 새로운 요구사항에 유연하게 대응
4. **성능 (Performance)**: 빠른 로딩과 부드러운 인터랙션
5. **명확성 (Clarity)**: 직관적이고 이해하기 쉬운 UI

## 🎨 색상 시스템

### Primary Colors
```scss
$primary-main: #FF5722;     // Deep Orange - 브랜드 아이덴티티
$primary-light: #FF8A65;    // 호버, 포커스 상태
$primary-dark: #E64A19;     // 액티브, 눌림 상태
```

### Secondary Colors
```scss
$secondary-main: #F89C26;   // Amber - 보조 액션
$secondary-light: #FFB74D;  // 호버 상태
$secondary-dark: #F57C00;   // 액티브 상태
```

### Semantic Colors
```scss
$success: #4CAF50;   // 성공, 완료, 긍정적 상태
$warning: #FF9800;   // 경고, 주의 필요
$error: #F44336;     // 오류, 위험, 부정적 상태
$info: #2196F3;      // 정보, 안내
```

### Grade Colors (등급 시스템)
```scss
$grade-s: #4CAF50;   // S등급 - 최우수
$grade-a+: #8BC34A;  // A+등급
$grade-a: #CDDC39;   // A등급
$grade-b: #FFC107;   // B등급
$grade-c: #FF9800;   // C등급
$grade-d: #F44336;   // D등급
```

### 색상 사용 가이드
- **Primary**: 주요 CTA, 브랜드 요소
- **Secondary**: 보조 액션, 강조 요소
- **Semantic**: 상태 표시, 피드백
- **Grades**: 성과 평가, 등급 표시

## 📏 타이포그래피

### 폰트 스택
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
             'Noto Sans KR', sans-serif;
```

### 타입 스케일
| Level | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|--------|
| H1 | 2.5rem (40px) | 700 | 1.2 | 페이지 제목 |
| H2 | 2rem (32px) | 600 | 1.3 | 섹션 제목 |
| H3 | 1.75rem (28px) | 600 | 1.4 | 서브섹션 |
| H4 | 1.5rem (24px) | 500 | 1.4 | 카드 제목 |
| H5 | 1.25rem (20px) | 500 | 1.5 | 소제목 |
| H6 | 1rem (16px) | 500 | 1.6 | 라벨 |
| Body1 | 1rem (16px) | 400 | 1.6 | 본문 |
| Body2 | 0.875rem (14px) | 400 | 1.6 | 보조 텍스트 |
| Caption | 0.75rem (12px) | 400 | 1.6 | 캡션, 힌트 |

## 📐 간격 시스템

### 기본 단위: 8px
```scss
$spacing-1: 4px;    // 최소 간격
$spacing-2: 8px;    // 기본 간격
$spacing-3: 12px;   // 컴포넌트 내부
$spacing-4: 16px;   // 컴포넌트 간
$spacing-5: 20px;   // 섹션 내부
$spacing-6: 24px;   // 섹션 간
$spacing-8: 32px;   // 페이지 여백
$spacing-10: 40px;  // 큰 섹션 간격
```

## 🎛️ 컴포넌트 라이브러리

### 버튼 (Buttons)
```javascript
// Primary Button
<Button variant="contained" color="primary">
  주요 액션
</Button>

// Secondary Button
<Button variant="outlined" color="secondary">
  보조 액션
</Button>

// Text Button
<Button variant="text">
  덜 중요한 액션
</Button>

// Icon Button
<IconButton color="primary">
  <DeleteIcon />
</IconButton>
```

#### 버튼 상태
- **Default**: 기본 상태
- **Hover**: 마우스 오버 시 밝아짐
- **Active**: 클릭 시 어두워짐
- **Disabled**: 비활성화 (opacity: 0.5)
- **Loading**: 로딩 스피너 표시

### 카드 (Cards)
```javascript
// 기본 카드
<Card>
  <CardContent>
    <Typography variant="h5">제목</Typography>
    <Typography>내용</Typography>
  </CardContent>
</Card>

// 데이터 카드
<DataCard
  title="총 직원"
  value="156"
  unit="명"
  icon={<PeopleIcon />}
  trend={{ type: 'up', label: '+12%' }}
/>

// 그라데이션 카드
<GradientCard>
  <CardContent>
    <Typography>특별 콘텐츠</Typography>
  </CardContent>
</GradientCard>
```

### 입력 필드 (Input Fields)
```javascript
// 기본 텍스트 필드
<TextField
  label="이름"
  variant="outlined"
  fullWidth
/>

// 선택 필드
<Select
  label="부서"
  value={department}
  onChange={handleChange}
>
  <MenuItem value="hr">인사부</MenuItem>
  <MenuItem value="dev">개발부</MenuItem>
</Select>

// 자동완성
<Autocomplete
  options={employees}
  renderInput={(params) => 
    <TextField {...params} label="직원 검색" />
  }
/>
```

### 테이블 (Tables)
```javascript
// 기본 테이블
<TableContainer component={Paper}>
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>이름</TableCell>
        <TableCell>부서</TableCell>
        <TableCell>등급</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {data.map((row) => (
        <TableRow key={row.id}>
          <TableCell>{row.name}</TableCell>
          <TableCell>{row.department}</TableCell>
          <TableCell>
            <GradeBadge grade={row.grade} />
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
</TableContainer>

// 고급 데이터 그리드
<DataGrid
  rows={data}
  columns={columns}
  pageSize={10}
  checkboxSelection
  disableSelectionOnClick
/>
```

### 다이얼로그 (Dialogs)
```javascript
<Dialog open={open} onClose={handleClose}>
  <DialogTitle>직원 상세 정보</DialogTitle>
  <DialogContent>
    <DialogContentText>
      직원의 상세 정보를 확인하세요.
    </DialogContentText>
    {/* 콘텐츠 */}
  </DialogContent>
  <DialogActions>
    <Button onClick={handleClose}>취소</Button>
    <Button onClick={handleConfirm} color="primary">
      확인
    </Button>
  </DialogActions>
</Dialog>
```

### 알림 (Alerts & Notifications)
```javascript
// 정보 알림
<Alert severity="info">
  새로운 업데이트가 있습니다.
</Alert>

// 성공 알림
<Alert severity="success">
  작업이 성공적으로 완료되었습니다.
</Alert>

// 경고 알림
<Alert severity="warning">
  주의가 필요한 사항입니다.
</Alert>

// 오류 알림
<Alert severity="error">
  오류가 발생했습니다.
</Alert>

// 스낵바 알림
<Snackbar
  open={open}
  autoHideDuration={6000}
  onClose={handleClose}
>
  <Alert severity="success">
    저장되었습니다!
  </Alert>
</Snackbar>
```

### 진행 표시기 (Progress Indicators)
```javascript
// 선형 진행률
<LinearProgress variant="determinate" value={75} />

// 원형 진행률
<CircularProgress />

// 진행률 카드
<ProgressCard
  title="프로젝트 진행률"
  value={45}
  total={60}
  color="primary"
/>
```

## 🎯 레이아웃 시스템

### Grid System
```javascript
<Grid container spacing={3}>
  <Grid item xs={12} sm={6} md={4} lg={3}>
    {/* 반응형 컬럼 */}
  </Grid>
</Grid>
```

### Container Sizes
- **xs**: 100% (모바일)
- **sm**: 600px
- **md**: 960px
- **lg**: 1280px
- **xl**: 1920px

### 레이아웃 패턴
```javascript
// 대시보드 레이아웃
<Box sx={{ display: 'flex' }}>
  <Drawer variant="permanent">
    {/* 사이드바 */}
  </Drawer>
  <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
    <Toolbar /> {/* 헤더 공간 */}
    {/* 메인 콘텐츠 */}
  </Box>
</Box>

// 카드 그리드 레이아웃
<Grid container spacing={3}>
  {cards.map((card) => (
    <Grid item xs={12} sm={6} md={4} key={card.id}>
      <Card>{/* 카드 내용 */}</Card>
    </Grid>
  ))}
</Grid>
```

## 🎭 애니메이션 & 트랜지션

### 트랜지션 타이밍
```scss
$transition-fast: 150ms;
$transition-normal: 300ms;
$transition-slow: 500ms;
```

### Easing Functions
```scss
$ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
$ease-out: cubic-bezier(0.0, 0, 0.2, 1);
$ease-in: cubic-bezier(0.4, 0, 1, 1);
$bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### 애니메이션 예제
```javascript
// Fade 애니메이션
<Fade in={visible} timeout={300}>
  <Card>{/* 콘텐츠 */}</Card>
</Fade>

// Grow 애니메이션
<Grow in={visible}>
  <Card>{/* 콘텐츠 */}</Card>
</Grow>

// Slide 애니메이션
<Slide direction="up" in={visible}>
  <Card>{/* 콘텐츠 */}</Card>
</Slide>

// 커스텀 애니메이션
<AnimatedContainer animation="zoom" delay={100}>
  <Card>{/* 콘텐츠 */}</Card>
</AnimatedContainer>
```

## 🌓 다크 모드

### 테마 전환
```javascript
const [darkMode, setDarkMode] = useState(false);

<ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
  <CssBaseline />
  {/* 앱 */}
</ThemeProvider>
```

### 다크 모드 색상
- Background: `#121212`
- Surface: `#1E1E1E`
- Primary Text: `#FFFFFF`
- Secondary Text: `#B0B0B0`

## ♿ 접근성 가이드라인

### WCAG 2.1 AA 준수
1. **색상 대비**: 최소 4.5:1 (일반 텍스트), 3:1 (큰 텍스트)
2. **키보드 네비게이션**: 모든 인터랙티브 요소 접근 가능
3. **스크린 리더**: 적절한 ARIA 라벨 제공
4. **포커스 표시**: 명확한 포커스 인디케이터

### 접근성 체크리스트
- [ ] 모든 이미지에 alt 텍스트
- [ ] 폼 필드에 라벨 연결
- [ ] 적절한 heading 계층 구조
- [ ] 키보드만으로 모든 기능 사용 가능
- [ ] 색상만으로 정보 전달 금지
- [ ] 에러 메시지 명확히 표시

## 📱 반응형 디자인

### Breakpoints
```javascript
const breakpoints = {
  xs: 0,     // 모바일
  sm: 600,   // 태블릿 세로
  md: 960,   // 태블릿 가로
  lg: 1280,  // 노트북
  xl: 1920,  // 데스크톱
};
```

### 반응형 유틸리티
```javascript
// 특정 화면 크기에서만 표시
<Box sx={{ display: { xs: 'none', md: 'block' } }}>
  {/* 태블릿 이상에서만 표시 */}
</Box>

// 반응형 간격
<Box sx={{ p: { xs: 2, sm: 3, md: 4 } }}>
  {/* 화면 크기별 패딩 */}
</Box>
```

## 🚀 성능 최적화

### 번들 크기 최적화
1. Tree shaking 활용
2. 동적 import 사용
3. 이미지 최적화 (WebP, lazy loading)
4. 폰트 최적화 (subset, preload)

### 렌더링 최적화
1. React.memo 활용
2. useMemo, useCallback 사용
3. Virtual scrolling (큰 리스트)
4. Debounce/Throttle 이벤트

## 📋 사용 예제

### 대시보드 페이지
```javascript
import React from 'react';
import { 
  Box, Grid, Typography, Paper 
} from '@mui/material';
import { 
  DataCard, ProgressCard, MetricCard 
} from '../components/common';

export default function Dashboard() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        AIRISS 대시보드
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} lg={3}>
          <DataCard
            title="총 직원"
            value="156"
            unit="명"
            icon={<PeopleIcon />}
            color="primary"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} lg={3}>
          <ProgressCard
            title="목표 달성률"
            percentage={78}
            color="success"
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <MetricCard
            title="주요 지표"
            metrics={[
              { label: '생산성', value: '92%', change: 5 },
              { label: '만족도', value: '4.5', change: 0.3 },
              { label: '이직률', value: '3.2%', change: -0.5 },
            ]}
          />
        </Grid>
      </Grid>
    </Box>
  );
}
```

## 🔄 버전 관리

### v4.0 (현재)
- Material-UI 통합
- 디자인 토큰 시스템
- 공통 컴포넌트 라이브러리
- 다크 모드 지원

### 향후 계획 (v4.1)
- 마이크로 인터랙션 추가
- 고급 데이터 시각화
- AI 기반 UI 추천
- 성능 모니터링 대시보드

## 📚 리소스

- [Material-UI 문서](https://mui.com/)
- [디자인 토큰](./tokens.js)
- [테마 설정](../src/theme/index.js)
- [공통 컴포넌트](../src/components/common/index.js)
- [마이그레이션 가이드](./MIGRATION_GUIDE.md)

## 💬 문의

디자인 시스템 관련 문의:
- Email: design-system@airiss.com
- Slack: #design-system
- GitHub: airiss/design-system