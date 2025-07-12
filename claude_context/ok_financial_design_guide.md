# OK금융그룹 디자인 가이드

## 🎨 브랜드 아이덴티티

### 핵심 브랜드 가치
- **신뢰성(Reliability)**: 금융의 기본, 안정감을 주는 디자인
- **혁신성(Innovation)**: AI 기술력, 미래지향적 인터페이스  
- **전문성(Professionalism)**: 정확하고 체계적인 정보 제공
- **접근성(Accessibility)**: 누구나 쉽게 사용할 수 있는 UX

### 브랜드 색상 팔레트

#### 주 색상 (Primary Colors)
```css
/* OK 코퍼레이트 블루 */
--ok-primary-blue: #1E3A8A;      /* 메인 브랜드 컬러 */
--ok-primary-blue-light: #3B82F6; /* 버튼, 링크 */
--ok-primary-blue-dark: #1E40AF;  /* 헤더, 중요 영역 */

/* OK 골드 액센트 */
--ok-gold: #F59E0B;               /* 강조, 알림 */
--ok-gold-light: #FCD34D;         /* 하이라이트 */
--ok-gold-dark: #D97706;          /* 액션 요소 */
```

#### 보조 색상 (Secondary Colors)
```css
/* 중성 색상 */
--ok-gray-50: #F8FAFC;            /* 배경 */
--ok-gray-100: #F1F5F9;           /* 카드 배경 */
--ok-gray-200: #E2E8F0;           /* 구분선 */
--ok-gray-300: #CBD5E1;           /* 비활성 요소 */
--ok-gray-400: #94A3B8;           /* 보조 텍스트 */
--ok-gray-500: #64748B;           /* 일반 텍스트 */
--ok-gray-600: #475569;           /* 진한 텍스트 */
--ok-gray-700: #334155;           /* 제목 */
--ok-gray-800: #1E293B;           /* 헤딩 */
--ok-gray-900: #0F172A;           /* 최고 강조 */

/* 시스템 색상 */
--ok-success: #10B981;            /* 성공, 완료 */
--ok-warning: #F59E0B;            /* 주의, 경고 */
--ok-error: #EF4444;              /* 오류, 위험 */
--ok-info: #3B82F6;               /* 정보, 안내 */
```

#### 성과 등급별 색상
```css
/* AIRISS 성과 등급 컬러 */
--grade-s: #10B981;               /* S등급: 에메랄드 */
--grade-a-plus: #059669;          /* A+등급: 진한 초록 */
--grade-a: #34D399;               /* A등급: 밝은 초록 */
--grade-b-plus: #60A5FA;          /* B+등급: 연한 파랑 */
--grade-b: #3B82F6;               /* B등급: 파랑 */
--grade-c: #F59E0B;               /* C등급: 주황 */
--grade-d: #EF4444;               /* D등급: 빨강 */
```

---

## 📝 타이포그래피

### 기본 폰트 패밀리
```css
/* 한글 + 영문 조합 */
font-family: 
  'Pretendard', 'Pretendard Variable',
  -apple-system, BlinkMacSystemFont, 
  'Segoe UI', 'Noto Sans KR', 
  Oxygen, Ubuntu, Cantarell, 
  'Helvetica Neue', sans-serif;

/* 숫자 전용 (성과 점수 등) */
font-family: 
  'SF Mono', 'Monaco', 'Inconsolata', 
  'Roboto Mono', 'Courier New', monospace;
```

### 타이포그래피 스케일
```css
/* 헤딩 */
.text-4xl { font-size: 2.25rem; line-height: 2.5rem; }    /* 주요 제목 */
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; }  /* 섹션 제목 */
.text-2xl { font-size: 1.5rem; line-height: 2rem; }       /* 카드 제목 */
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }    /* 서브 제목 */
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }   /* 중요 텍스트 */

/* 본문 */
.text-base { font-size: 1rem; line-height: 1.5rem; }      /* 기본 텍스트 */
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }   /* 보조 텍스트 */
.text-xs { font-size: 0.75rem; line-height: 1rem; }       /* 캡션, 레이블 */

/* 폰트 굵기 */
.font-thin { font-weight: 100; }
.font-light { font-weight: 300; }
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }    /* 권장: 일반 강조 */
.font-semibold { font-weight: 600; }  /* 권장: 제목 */
.font-bold { font-weight: 700; }      /* 권장: 중요 제목 */
.font-extrabold { font-weight: 800; }
.font-black { font-weight: 900; }
```

---

## 🎛️ UI 컴포넌트 스타일

### 버튼 스타일
```css
/* 주요 액션 버튼 */
.btn-primary {
  background-color: var(--ok-primary-blue);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: var(--ok-primary-blue-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(30, 58, 138, 0.25);
}

/* 보조 버튼 */
.btn-secondary {
  background-color: white;
  color: var(--ok-primary-blue);
  border: 2px solid var(--ok-primary-blue);
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--ok-primary-blue);
  color: white;
}

/* 골드 액센트 버튼 */
.btn-accent {
  background-color: var(--ok-gold);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-accent:hover {
  background-color: var(--ok-gold-dark);
}
```

### 카드 스타일
```css
/* 기본 카드 */
.card {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid var(--ok-gray-200);
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

/* 성과 카드 */
.performance-card {
  background: linear-gradient(135deg, var(--ok-primary-blue) 0%, var(--ok-primary-blue-light) 100%);
  color: white;
  padding: 2rem;
  border-radius: 1rem;
  position: relative;
  overflow: hidden;
}

.performance-card::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: var(--ok-gold);
  border-radius: 50%;
  transform: translate(30px, -30px);
  opacity: 0.1;
}
```

### 입력 필드
```css
/* 기본 입력 필드 */
.input-field {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid var(--ok-gray-300);
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: all 0.2s ease;
  background-color: white;
}

.input-field:focus {
  outline: none;
  border-color: var(--ok-primary-blue);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-field:error {
  border-color: var(--ok-error);
}

/* 파일 업로드 영역 */
.upload-zone {
  border: 2px dashed var(--ok-gray-300);
  border-radius: 0.75rem;
  padding: 3rem 2rem;
  text-align: center;
  transition: all 0.2s ease;
  cursor: pointer;
}

.upload-zone:hover,
.upload-zone.dragover {
  border-color: var(--ok-primary-blue);
  background-color: var(--ok-gray-50);
}
```

---

## 📊 데이터 시각화 스타일

### Chart.js 커스텀 테마
```javascript
const okChartTheme = {
  // 차트 기본 색상 팔레트
  colors: [
    '#1E3A8A',  // OK 블루
    '#F59E0B',  // OK 골드
    '#10B981',  // 성공 그린
    '#3B82F6',  // 라이트 블루
    '#EF4444',  // 에러 레드
    '#8B5CF6',  // 퍼플
    '#F97316',  // 오렌지
    '#06B6D4'   // 시안
  ],
  
  // 폰트 설정
  fonts: {
    family: 'Pretendard, -apple-system, sans-serif',
    size: 12,
    weight: '500'
  },
  
  // 그리드 스타일
  grid: {
    color: '#E2E8F0',
    lineWidth: 1
  },
  
  // 범례 스타일
  legend: {
    position: 'bottom',
    labels: {
      usePointStyle: true,
      padding: 20,
      font: {
        size: 12,
        family: 'Pretendard, sans-serif'
      }
    }
  }
};

// 레이더 차트 (8대 차원) 전용 스타일
const radarChartStyle = {
  backgroundColor: 'rgba(30, 58, 138, 0.1)',
  borderColor: '#1E3A8A',
  borderWidth: 2,
  pointBackgroundColor: '#1E3A8A',
  pointBorderColor: '#ffffff',
  pointBorderWidth: 2,
  pointRadius: 5
};
```

### 성과 등급 표시
```css
/* 등급 배지 */
.grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  font-weight: 700;
  font-size: 1rem;
  color: white;
  margin-right: 0.5rem;
}

.grade-s { background-color: var(--grade-s); }
.grade-a-plus { background-color: var(--grade-a-plus); }
.grade-a { background-color: var(--grade-a); }
.grade-b-plus { background-color: var(--grade-b-plus); }
.grade-b { background-color: var(--grade-b); }
.grade-c { background-color: var(--grade-c); }
.grade-d { background-color: var(--grade-d); }

/* 점수 표시 */
.score-display {
  font-family: 'SF Mono', monospace;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--ok-primary-blue);
  text-align: center;
  margin: 1rem 0;
}

.score-display .unit {
  font-size: 1rem;
  color: var(--ok-gray-500);
  margin-left: 0.25rem;
}
```

---

## 🔍 반응형 디자인 가이드

### 브레이크포인트
```css
/* OK금융그룹 표준 브레이크포인트 */
:root {
  --breakpoint-sm: 640px;   /* 모바일 */
  --breakpoint-md: 768px;   /* 태블릿 */
  --breakpoint-lg: 1024px;  /* 데스크톱 */
  --breakpoint-xl: 1280px;  /* 대형 모니터 */
  --breakpoint-2xl: 1536px; /* 4K 모니터 */
}

/* 반응형 유틸리티 */
@media (max-width: 640px) {
  .container { padding: 1rem; }
  .card { padding: 1rem; }
  .text-4xl { font-size: 1.875rem; }
  .text-3xl { font-size: 1.5rem; }
}

@media (min-width: 641px) and (max-width: 1024px) {
  .container { padding: 1.5rem; }
  .grid-cols-auto { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1025px) {
  .container { padding: 2rem; }
  .grid-cols-auto { grid-template-columns: repeat(3, 1fr); }
}
```

### 모바일 우선 가이드라인
```css
/* 모바일 터치 타겟 */
.touch-target {
  min-height: 44px;  /* Apple 가이드라인 */
  min-width: 44px;
  padding: 0.75rem;
}

/* 가독성 최적화 */
.mobile-optimized {
  font-size: 16px;      /* iOS 줌 방지 */
  line-height: 1.6;     /* 가독성 향상 */
  letter-spacing: -0.01em; /* 한글 최적화 */
}
```

---

## 🎭 애니메이션 및 인터랙션

### 표준 애니메이션
```css
/* 부드러운 전환 */
.smooth-transition {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 호버 효과 */
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

/* 로딩 애니메이션 */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.loading-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* 나타남 효과 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in-up {
  animation: fadeInUp 0.6s ease-out;
}
```

### 마이크로 인터랙션
```css
/* 버튼 클릭 피드백 */
.btn-feedback:active {
  transform: scale(0.98);
}

/* 입력 필드 포커스 */
.input-focus {
  position: relative;
}

.input-focus::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background-color: var(--ok-primary-blue);
  transition: width 0.3s ease;
}

.input-focus:focus-within::after {
  width: 100%;
}
```

---

## 🚨 상태 및 알림 디자인

### 알림 스타일
```css
/* 성공 알림 */
.alert-success {
  background-color: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: var(--ok-success);
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  border-left: 4px solid var(--ok-success);
}

/* 경고 알림 */
.alert-warning {
  background-color: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
  color: var(--ok-warning);
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  border-left: 4px solid var(--ok-warning);
}

/* 오류 알림 */
.alert-error {
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--ok-error);
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  border-left: 4px solid var(--ok-error);
}

/* 정보 알림 */
.alert-info {
  background-color: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: var(--ok-info);
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  border-left: 4px solid var(--ok-info);
}
```

### 로딩 상태
```css
/* 진행률 표시 */
.progress-bar {
  width: 100%;
  height: 8px;
  background-color: var(--ok-gray-200);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--ok-primary-blue), var(--ok-gold));
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* 스피너 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--ok-gray-300);
  border-top: 2px solid var(--ok-primary-blue);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
```

---

## 📱 모바일 최적화

### 터치 인터페이스
```css
/* 터치 친화적 버튼 */
.mobile-button {
  min-height: 48px;
  min-width: 48px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border-radius: 0.5rem;
  touch-action: manipulation; /* 더블탭 줌 방지 */
}

/* 스와이프 제스처 힌트 */
.swipeable {
  position: relative;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}

.swipeable::after {
  content: '← 좌우로 스와이프';
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 0.75rem;
  color: var(--ok-gray-400);
  opacity: 0;
  animation: fadeInOut 3s ease-in-out;
}

@keyframes fadeInOut {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}
```

---

## 🔧 구현 가이드라인

### HTML 구조 원칙
```html
<!-- 시맨틱 마크업 사용 -->
<main class="dashboard">
  <header class="dashboard-header">
    <h1 class="sr-only">AIRISS 대시보드</h1>
  </header>
  
  <section class="performance-overview" aria-labelledby="performance-title">
    <h2 id="performance-title">성과 개요</h2>
    <!-- 콘텐츠 -->
  </section>
  
  <section class="analysis-results" aria-labelledby="results-title">
    <h2 id="results-title">분석 결과</h2>
    <!-- 콘텐츠 -->
  </section>
</main>
```

### CSS 클래스 네이밍
```css
/* BEM 방법론 사용 */
.component {}                  /* Block */
.component__element {}         /* Element */
.component--modifier {}        /* Modifier */

/* 예시 */
.performance-card {}
.performance-card__header {}
.performance-card__score {}
.performance-card--highlighted {}
```

### 접근성 고려사항
```css
/* 포커스 표시 */
.focus-visible:focus {
  outline: 2px solid var(--ok-primary-blue);
  outline-offset: 2px;
}

/* 스크린 리더 전용 텍스트 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 고대비 모드 지원 */
@media (prefers-contrast: high) {
  .card {
    border: 2px solid var(--ok-gray-800);
  }
}

/* 애니메이션 비활성화 옵션 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 🎯 AIRISS 전용 컴포넌트

### 성과 점수 표시 컴포넌트
```css
.airiss-score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, 
    var(--ok-primary-blue) 0%, 
    var(--ok-primary-blue-light) 100%);
  border-radius: 1rem;
  color: white;
  text-align: center;
}

.airiss-score-display__score {
  font-size: 4rem;
  font-weight: 900;
  font-family: 'SF Mono', monospace;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.airiss-score-display__grade {
  font-size: 1.25rem;
  font-weight: 600;
  opacity: 0.9;
}

.airiss-score-display__label {
  font-size: 0.875rem;
  opacity: 0.7;
  margin-top: 0.5rem;
}
```

### 8대 차원 레이더 차트 컨테이너
```css
.airiss-radar-container {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.airiss-radar-container__title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--ok-gray-800);
  margin-bottom: 1.5rem;
  text-align: center;
}

.airiss-radar-container__chart {
  position: relative;
  height: 400px;
  margin-bottom: 1rem;
}

.airiss-radar-container__legend {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}
```

---

## 📋 체크리스트

### 디자인 구현 전 확인사항
- [ ] OK금융그룹 브랜드 색상 사용
- [ ] Pretendard 폰트 적용
- [ ] 반응형 디자인 고려
- [ ] 접근성 기준 준수
- [ ] 터치 인터페이스 최적화
- [ ] 로딩 상태 처리
- [ ] 에러 상태 처리
- [ ] 다크모드 호환성 (선택사항)

### 성능 고려사항
- [ ] 이미지 최적화 (WebP, 적절한 크기)
- [ ] CSS 번들 크기 최소화
- [ ] 중요 스타일 인라인 처리
- [ ] 애니메이션 성능 최적화
- [ ] 폰트 로딩 최적화

---

**"일관된 브랜드 경험과 직관적인 사용성이 AIRISS의 핵심입니다!"** 🎨