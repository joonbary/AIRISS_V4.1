# AIRISS 프론트엔드 개발 가이드

## 🎯 프론트엔드 아키텍처 개요

### 기술 스택
```
Core Framework: React 18.2+
Build Tool: Create React App (CRA)
State Management: React Hooks (useState, useContext)
HTTP Client: Fetch API + Custom hooks
Real-time: WebSocket (native)
Charts: Chart.js 4.4+
Styling: CSS Modules + Tailwind CSS
Icons: Lucide React
Development: VS Code + ES6+ + JSX
```

### 프로젝트 구조
```
airiss-v4-frontend/
├── public/
│   ├── index.html           # 기본 HTML 템플릿
│   ├── manifest.json        # PWA 설정
│   ├── favicon.ico          # 파비콘
│   └── icons/              # 앱 아이콘들
│
├── src/
│   ├── components/         # 재사용 가능한 컴포넌트
│   │   ├── common/         # 공통 컴포넌트
│   │   ├── charts/         # 차트 컴포넌트들
│   │   ├── dashboard/      # 대시보드 전용
│   │   └── forms/          # 폼 관련
│   │
│   ├── hooks/              # 커스텀 React Hooks
│   │   ├── useAnalysis.js  # 분석 관련 로직
│   │   ├── useWebSocket.js # WebSocket 연결
│   │   └── useFileUpload.js # 파일 업로드
│   │
│   ├── services/           # API 및 비즈니스 로직
│   │   ├── api.js          # HTTP API 클라이언트
│   │   ├── websocket.js    # WebSocket 매니저
│   │   └── storage.js      # 로컬 스토리지
│   │
│   ├── utils/              # 유틸리티 함수들
│   │   ├── formatters.js   # 데이터 포맷팅
│   │   ├── validators.js   # 입력 검증
│   │   └── constants.js    # 상수 정의
│   │
│   ├── styles/             # 스타일 파일들
│   │   ├── globals.css     # 전역 스타일
│   │   ├── variables.css   # CSS 변수
│   │   └── components/     # 컴포넌트별 스타일
│   │
│   ├── contexts/           # React Context들
│   │   ├── AuthContext.js  # 인증 상태
│   │   └── ThemeContext.js # 테마 설정
│   │
│   ├── App.js              # 메인 앱 컴포넌트
│   ├── index.js            # 엔트리 포인트
│   └── reportWebVitals.js  # 성능 측정
│
├── package.json            # 의존성 관리
├── tailwind.config.js      # Tailwind 설정
└── .env.local             # 환경변수 (로컬)
```

---

## 🧩 핵심 컴포넌트 가이드

### 1. Dashboard 컴포넌트
```jsx
// src/components/dashboard/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { useAnalysis } from '../../hooks/useAnalysis';
import { useWebSocket } from '../../hooks/useWebSocket';
import RadarChart from '../charts/RadarChart';
import ScoreCard from '../common/ScoreCard';
import ProgressBar from '../common/ProgressBar';

const Dashboard = () => {
  const { analysisData, loading, error } = useAnalysis();
  const { connectionStatus, lastMessage } = useWebSocket();

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1 className="text-3xl font-bold text-ok-primary-blue">
          AIRISS 인재 분석 대시보드
        </h1>
        <ConnectionStatus status={connectionStatus} />
      </header>

      <main className="dashboard-content">
        {/* 성과 개요 섹션 */}
        <section className="performance-overview">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <ScoreCard
              title="종합 점수"
              score={analysisData?.overallScore}
              grade={analysisData?.grade}
              trend={analysisData?.trend}
            />
            {/* 추가 카드들 */}
          </div>
        </section>

        {/* 차트 섹션 */}
        <section className="charts-section">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <RadarChart 
              data={analysisData?.dimensionScores}
              title="8대 핵심 역량"
            />
            {/* 추가 차트들 */}
          </div>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;
```

### 2. 파일 업로드 컴포넌트
```jsx
// src/components/forms/FileUpload.jsx
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { useFileUpload } from '../../hooks/useFileUpload';

const FileUpload = ({ onUploadComplete }) => {
  const [dragActive, setDragActive] = useState(false);
  const { uploadFile, uploading, progress, error } = useFileUpload();

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      try {
        const result = await uploadFile(file);
        onUploadComplete(result);
      } catch (err) {
        console.error('Upload failed:', err);
      }
    }
  }, [uploadFile, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024 // 50MB
  });

  return (
    <div className="upload-container">
      <div
        {...getRootProps()}
        className={`upload-zone ${isDragActive ? 'dragover' : ''} ${uploading ? 'uploading' : ''}`}
      >
        <input {...getInputProps()} />
        
        {uploading ? (
          <div className="upload-progress">
            <div className="spinner" />
            <p>파일 업로드 중... {Math.round(progress)}%</p>
            <ProgressBar value={progress} />
          </div>
        ) : (
          <div className="upload-content">
            <Upload size={48} className="text-ok-primary-blue mb-4" />
            <p className="text-lg font-medium mb-2">
              파일을 드래그하거나 클릭하여 업로드
            </p>
            <p className="text-sm text-gray-500">
              CSV, Excel 파일 지원 (최대 50MB)
            </p>
          </div>
        )}
      </div>

      {error && (
        <div className="alert-error mt-4">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
```

### 3. Chart.js 래퍼 컴포넌트
```jsx
// src/components/charts/RadarChart.jsx
import React, { useRef, useEffect } from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Radar } from 'react-chartjs-2';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const RadarChart = ({ data, title }) => {
  const chartRef = useRef();

  const chartData = {
    labels: [
      '업무성과', '리더십협업', '커뮤니케이션', '전문성학습',
      '태도열정', '혁신창의', '고객지향', '윤리준수'
    ],
    datasets: [
      {
        label: '현재 점수',
        data: data || [0, 0, 0, 0, 0, 0, 0, 0],
        backgroundColor: 'rgba(30, 58, 138, 0.2)',
        borderColor: 'rgba(30, 58, 138, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(30, 58, 138, 1)',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5,
      }
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        min: 0,
        ticks: {
          stepSize: 20,
          callback: function(value) {
            return value + '점';
          }
        },
        grid: {
          color: '#E2E8F0',
        },
        angleLines: {
          color: '#E2E8F0',
        },
        pointLabels: {
          font: {
            size: 12,
            family: 'Pretendard, sans-serif'
          },
          color: '#374151'
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        titleColor: '#374151',
        bodyColor: '#374151',
        borderColor: '#E2E8F0',
        borderWidth: 1,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.parsed.r}점`;
          }
        }
      }
    },
    elements: {
      point: {
        hoverRadius: 8
      }
    }
  };

  return (
    <div className="airiss-radar-container">
      <h3 className="airiss-radar-container__title">{title}</h3>
      <div className="airiss-radar-container__chart">
        <Radar ref={chartRef} data={chartData} options={chartOptions} />
      </div>
    </div>
  );
};

export default RadarChart;
```

---

## 🔗 커스텀 Hooks

### 1. useAnalysis Hook
```jsx
// src/hooks/useAnalysis.js
import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';

export const useAnalysis = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const startAnalysis = useCallback(async (fileId) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.startAnalysis(fileId);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchAnalysisResult = useCallback(async (fileId) => {
    try {
      const result = await apiService.getAnalysisResult(fileId);
      setAnalysisData(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const clearAnalysis = useCallback(() => {
    setAnalysisData(null);
    setError(null);
  }, []);

  return {
    analysisData,
    loading,
    error,
    startAnalysis,
    fetchAnalysisResult,
    clearAnalysis
  };
};
```

### 2. useWebSocket Hook
```jsx
// src/hooks/useWebSocket.js
import { useState, useEffect, useRef, useCallback } from 'react';

export const useWebSocket = (url) => {
  const [connectionStatus, setConnectionStatus] = useState('Connecting');
  const [lastMessage, setLastMessage] = useState(null);
  const ws = useRef(null);

  const connect = useCallback(() => {
    const wsUrl = url || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/websocket`;
    
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setConnectionStatus('Connected');
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setLastMessage(message);
    };

    ws.current.onclose = () => {
      setConnectionStatus('Disconnected');
      console.log('WebSocket disconnected');
      
      // 자동 재연결 (5초 후)
      setTimeout(() => {
        if (ws.current?.readyState === WebSocket.CLOSED) {
          connect();
        }
      }, 5000);
    };

    ws.current.onerror = (error) => {
      setConnectionStatus('Error');
      console.error('WebSocket error:', error);
    };
  }, [url]);

  const sendMessage = useCallback((message) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  }, []);

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close();
    }
  }, []);

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    connectionStatus,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect: connect
  };
};
```

### 3. useFileUpload Hook
```jsx
// src/hooks/useFileUpload.js
import { useState, useCallback } from 'react';
import { apiService } from '../services/api';

export const useFileUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const uploadFile = useCallback(async (file) => {
    setUploading(true);
    setProgress(0);
    setError(null);

    try {
      // 파일 검증
      if (!file) {
        throw new Error('파일을 선택해주세요.');
      }

      if (file.size > 50 * 1024 * 1024) { // 50MB
        throw new Error('파일 크기가 50MB를 초과합니다.');
      }

      const allowedTypes = [
        'text/csv',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
      ];

      if (!allowedTypes.includes(file.type)) {
        throw new Error('CSV 또는 Excel 파일만 업로드 가능합니다.');
      }

      // FormData 생성
      const formData = new FormData();
      formData.append('file', file);

      // 업로드 진행률 추적
      const xhr = new XMLHttpRequest();

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          setProgress(percentComplete);
        }
      };

      // Promise로 래핑
      const uploadPromise = new Promise((resolve, reject) => {
        xhr.onload = () => {
          if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } else {
            reject(new Error(`업로드 실패: ${xhr.statusText}`));
          }
        };

        xhr.onerror = () => {
          reject(new Error('네트워크 오류가 발생했습니다.'));
        };

        xhr.open('POST', '/api/upload');
        xhr.send(formData);
      });

      const result = await uploadPromise;
      setProgress(100);
      
      return result;

    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setUploading(false);
    }
  }, []);

  const resetUpload = useCallback(() => {
    setUploading(false);
    setProgress(0);
    setError(null);
  }, []);

  return {
    uploadFile,
    uploading,
    progress,
    error,
    resetUpload
  };
};
```

---

## 🔧 API 서비스 레이어

### API 클라이언트
```javascript
// src/services/api.js
class ApiService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || '';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // 파일 업로드
  async uploadFile(formData) {
    return this.request('/api/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // FormData는 Content-Type 자동 설정
    });
  }

  // 분석 시작
  async startAnalysis(fileId) {
    return this.request(`/api/analysis/${fileId}`, {
      method: 'POST',
    });
  }

  // 분석 상태 조회
  async getAnalysisStatus(fileId) {
    return this.request(`/api/analysis/${fileId}/status`);
  }

  // 분석 결과 조회
  async getAnalysisResult(fileId) {
    return this.request(`/api/analysis/${fileId}/result`);
  }

  // 저장된 분석 목록
  async getSavedAnalyses(page = 1, limit = 10) {
    return this.request(`/api/analysis-storage?page=${page}&limit=${limit}`);
  }

  // 분석 저장
  async saveAnalysis(fileId, analysisData) {
    return this.request('/api/analysis-storage', {
      method: 'POST',
      body: JSON.stringify({
        file_id: fileId,
        analysis_data: analysisData,
      }),
    });
  }

  // 분석 삭제
  async deleteAnalysis(analysisId) {
    return this.request(`/api/analysis-storage/${analysisId}`, {
      method: 'DELETE',
    });
  }

  // 건강 상태 확인
  async healthCheck() {
    return this.request('/health');
  }
}

export const apiService = new ApiService();
```

---

## 🎨 스타일링 가이드

### Tailwind CSS 설정
```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ok-primary-blue': '#1E3A8A',
        'ok-primary-blue-light': '#3B82F6',
        'ok-primary-blue-dark': '#1E40AF',
        'ok-gold': '#F59E0B',
        'ok-gold-light': '#FCD34D',
        'ok-gold-dark': '#D97706',
        'ok-success': '#10B981',
        'ok-warning': '#F59E0B',
        'ok-error': '#EF4444',
        'ok-info': '#3B82F6',
      },
      fontFamily: {
        'sans': ['Pretendard', 'system-ui', 'sans-serif'],
        'mono': ['SF Mono', 'Monaco', 'Courier New', 'monospace'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.6s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeInUp: {
          '0%': {
            opacity: '0',
            transform: 'translateY(20px)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### 글로벌 CSS 변수
```css
/* src/styles/globals.css */
:root {
  /* OK 금융그룹 브랜드 색상 */
  --ok-primary-blue: #1E3A8A;
  --ok-primary-blue-light: #3B82F6;
  --ok-primary-blue-dark: #1E40AF;
  --ok-gold: #F59E0B;
  --ok-gold-light: #FCD34D;
  --ok-gold-dark: #D97706;

  /* 시스템 색상 */
  --ok-success: #10B981;
  --ok-warning: #F59E0B;
  --ok-error: #EF4444;
  --ok-info: #3B82F6;

  /* 중성 색상 */
  --ok-gray-50: #F8FAFC;
  --ok-gray-100: #F1F5F9;
  --ok-gray-200: #E2E8F0;
  --ok-gray-300: #CBD5E1;
  --ok-gray-400: #94A3B8;
  --ok-gray-500: #64748B;
  --ok-gray-600: #475569;
  --ok-gray-700: #334155;
  --ok-gray-800: #1E293B;
  --ok-gray-900: #0F172A;

  /* 성과 등급 색상 */
  --grade-s: #10B981;
  --grade-a-plus: #059669;
  --grade-a: #34D399;
  --grade-b-plus: #60A5FA;
  --grade-b: #3B82F6;
  --grade-c: #F59E0B;
  --grade-d: #EF4444;

  /* 레이아웃 */
  --header-height: 4rem;
  --sidebar-width: 16rem;
  --content-max-width: 1200px;

  /* 애니메이션 */
  --transition-fast: 0.15s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.5s ease;
}

/* 다크 모드 지원 (선택사항) */
@media (prefers-color-scheme: dark) {
  :root {
    --ok-gray-50: #0F172A;
    --ok-gray-100: #1E293B;
    --ok-gray-200: #334155;
  }
}

/* 기본 스타일 재설정 */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--ok-gray-50);
  color: var(--ok-gray-900);
}

/* 스크롤바 스타일링 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: var(--ok-gray-100);
}

::-webkit-scrollbar-thumb {
  background: var(--ok-gray-300);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--ok-gray-400);
}

/* 포커스 스타일 */
*:focus {
  outline: 2px solid var(--ok-primary-blue);
  outline-offset: 2px;
}

/* 선택 텍스트 스타일 */
::selection {
  background-color: var(--ok-primary-blue);
  color: white;
}
```

---

## 📱 반응형 디자인 패턴

### 그리드 레이아웃
```jsx
// 반응형 대시보드 레이아웃
const DashboardLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-ok-gray-50">
      {/* 헤더 */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-ok-primary-blue">AIRISS</h1>
            </div>
            <nav className="hidden md:flex space-x-8">
              <a href="#dashboard" className="text-ok-gray-600 hover:text-ok-primary-blue">
                대시보드
              </a>
              <a href="#analysis" className="text-ok-gray-600 hover:text-ok-primary-blue">
                분석
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  );
};
```

### 모바일 우선 컴포넌트
```jsx
// 반응형 카드 그리드
const ResponsiveCardGrid = ({ cards }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
      {cards.map((card, index) => (
        <div
          key={index}
          className="bg-white rounded-lg shadow-sm border border-ok-gray-200 p-4 sm:p-6 hover:shadow-md transition-shadow"
        >
          {card.content}
        </div>
      ))}
    </div>
  );
};

// 반응형 차트 컨테이너
const ResponsiveChartContainer = ({ children, title }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-ok-gray-200 p-4 sm:p-6">
      <h3 className="text-lg sm:text-xl font-semibold text-ok-gray-800 mb-4 sm:mb-6">
        {title}
      </h3>
      <div className="h-64 sm:h-80 lg:h-96">
        {children}
      </div>
    </div>
  );
};
```

---

## 🔧 개발 환경 설정

### package.json 의존성
```json
{
  "name": "airiss-v4-frontend",
  "version": "4.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "lucide-react": "^0.263.1",
    "react-dropzone": "^14.2.3",
    "web-vitals": "^3.3.2"
  },
  "devDependencies": {
    "@tailwindcss/forms": "^0.5.6",
    "@tailwindcss/typography": "^0.5.10",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.24"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "build:prod": "NODE_ENV=production npm run build",
    "analyze": "npm run build && npx source-map-explorer 'build/static/js/*.js'"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:8002"
}
```

### 환경변수 설정
```bash
# .env.local
REACT_APP_API_URL=http://localhost:8002
REACT_APP_WS_URL=ws://localhost:8002/websocket
REACT_APP_VERSION=4.1.0
REACT_APP_BUILD_DATE=2024-01-15

# .env.production
REACT_APP_API_URL=https://web-production-4066.up.railway.app
REACT_APP_WS_URL=wss://web-production-4066.up.railway.app/websocket
REACT_APP_VERSION=4.1.0
```

---

## 🚀 성능 최적화

### 코드 분할 (Code Splitting)
```jsx
// 지연 로딩을 위한 동적 import
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./components/dashboard/Dashboard'));
const AnalysisResults = lazy(() => import('./components/analysis/AnalysisResults'));

function App() {
  return (
    <div className="App">
      <Suspense fallback={<div className="loading-spinner">로딩 중...</div>}>
        <Dashboard />
      </Suspense>
    </div>
  );
}
```

### 메모이제이션
```jsx
// React.memo로 불필요한 리렌더링 방지
import React, { memo, useMemo } from 'react';

const ScoreCard = memo(({ title, score, grade, trend }) => {
  const formattedScore = useMemo(() => {
    return score ? score.toFixed(1) : '0.0';
  }, [score]);

  const gradeColor = useMemo(() => {
    const gradeColors = {
      'S': 'var(--grade-s)',
      'A+': 'var(--grade-a-plus)',
      'A': 'var(--grade-a)',
      'B+': 'var(--grade-b-plus)',
      'B': 'var(--grade-b)',
      'C': 'var(--grade-c)',
      'D': 'var(--grade-d)'
    };
    return gradeColors[grade] || 'var(--ok-gray-400)';
  }, [grade]);

  return (
    <div className="score-card">
      {/* 컴포넌트 내용 */}
    </div>
  );
});

export default ScoreCard;
```

### 이미지 최적화
```jsx
// 이미지 지연 로딩
const LazyImage = ({ src, alt, className }) => {
  const [loaded, setLoaded] = useState(false);
  const [inView, setInView] = useState(false);
  const imgRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={imgRef} className={className}>
      {inView && (
        <img
          src={src}
          alt={alt}
          loading="lazy"
          onLoad={() => setLoaded(true)}
          className={`transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
        />
      )}
    </div>
  );
};
```

---

## 🧪 테스트 가이드

### Jest + React Testing Library
```jsx
// src/components/__tests__/ScoreCard.test.js
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScoreCard from '../common/ScoreCard';

describe('ScoreCard', () => {
  const defaultProps = {
    title: '종합 점수',
    score: 85.5,
    grade: 'A',
    trend: 'up'
  };

  test('제목과 점수가 올바르게 표시된다', () => {
    render(<ScoreCard {...defaultProps} />);
    
    expect(screen.getByText('종합 점수')).toBeInTheDocument();
    expect(screen.getByText('85.5')).toBeInTheDocument();
    expect(screen.getByText('A')).toBeInTheDocument();
  });

  test('등급에 따라 올바른 색상이 적용된다', () => {
    render(<ScoreCard {...defaultProps} />);
    
    const gradeElement = screen.getByText('A');
    expect(gradeElement).toHaveClass('grade-a');
  });

  test('점수가 없을 때 기본값이 표시된다', () => {
    render(<ScoreCard {...defaultProps} score={null} />);
    
    expect(screen.getByText('0.0')).toBeInTheDocument();
  });
});
```

---

## 📋 체크리스트

### 개발 전 확인사항
- [ ] Node.js 18+ 설치
- [ ] npm/yarn 최신 버전
- [ ] VS Code + React 확장팩
- [ ] Git 설정 완료

### 컴포넌트 개발 시
- [ ] PropTypes 또는 TypeScript 타입 정의
- [ ] 접근성 고려 (ARIA 라벨, 키보드 네비게이션)
- [ ] 반응형 디자인 적용
- [ ] 에러 바운더리 처리
- [ ] 로딩 상태 처리
- [ ] 메모이제이션 적용 (필요시)

### 배포 전 확인사항
- [ ] 빌드 에러 없음
- [ ] 테스트 통과
- [ ] 성능 최적화 적용
- [ ] 브라우저 호환성 확인
- [ ] 접근성 검증
- [ ] SEO 메타데이터 설정

---

**"컴포넌트 기반 개발로 재사용성과 유지보수성을 극대화합니다!"** ⚛️